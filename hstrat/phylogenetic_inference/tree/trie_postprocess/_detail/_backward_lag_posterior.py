"""Posterior divergence times under a power-law prior over backward lag from
nodes' mismatch bounds, given spurious differentia collisions."""

import logging
import types
import typing

import numpy as np
import polars as pl

from ....._auxiliary_lib import jit, log_context_duration
from ._comparable_ranks import (
    first_retained_between,
    iter_retained_ranks,
    mark_inner_node_bounds,
)


def _calc_prior_moments(
    a: np.ndarray, b: np.ndarray, hi: np.ndarray, alpha: float
) -> typing.Tuple[np.ndarray, np.ndarray]:
    """Prior mass and mean of divergence generation `t` within intervals
    [`a`, `b`), for prior density proportional to `u ** -alpha` over
    backward lag `u = H - t + 1` from the node's mismatch bound
    `H = max(hi, 1)`, so that `u = 1` at the top of every node's own
    interval.

    Gives mass `b - a` and mean `(a + b - 1) / 2` for `alpha == 0`. Means
    are clipped to within intervals' generations.
    """
    H = np.maximum(hi, 1.0)
    u1 = H - b + 1.0
    u2 = H - a + 1.0
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        if abs(alpha) < 1e-9:
            mass = u2 - u1
            mean_u = (u1 + u2) / 2
        elif abs(alpha - 1) < 1e-9:
            mass = np.log(u2 / u1)
            mean_u = (u2 - u1) / mass
        elif abs(alpha - 2) < 1e-9:
            mass = 1 / u1 - 1 / u2
            mean_u = np.log(u2 / u1) / mass
        else:
            mass = (u2 ** (1 - alpha) - u1 ** (1 - alpha)) / (1 - alpha)
            moment = (u2 ** (2 - alpha) - u1 ** (2 - alpha)) / (2 - alpha)
            mean_u = moment / mass
    is_empty = b <= a
    mean = np.clip(H + 0.5 - mean_u, a, np.maximum(a, b - 1))
    return (
        np.where(is_empty, 0.0, mass),
        np.where(is_empty | ~np.isfinite(mean), (a + b - 1) / 2, mean),
    )


def _calc_chunk_means_grid(
    retained: np.ndarray,
    ranks: np.ndarray,
    youngest_T: np.ndarray,
    p: float,
    dstream_S: int,
    alphas: np.ndarray,
) -> np.ndarray:
    """Posterior mean divergence times, relative to `dstream_S`, for a chunk
    of inner nodes (rows) and prior exponents `alphas` (columns), given
    sorted ranks `retained` at their comparison `dstream_T`."""
    # node's own interval: from node rank to first comparable rank after,
    # or to youngest tip if none; divergence cannot precede dstream_S
    (first_shared,) = first_retained_between(
        retained, ranks, youngest_T, num=1
    ).T
    first_shared = np.where(
        np.isfinite(first_shared), first_shared, youngest_T
    )
    lo = np.maximum(ranks - dstream_S, 0)
    hi = np.maximum(first_shared - dstream_S, 0)

    # earlier intervals: between successive comparable ranks before node
    # rank, back to dstream_S, latest first; divergence in the jth requires
    # j spurious collisions, at its upper bound and each later comparable
    # rank up to and including node rank
    earlier = np.where(retained < ranks[:, None], retained, -np.inf)
    earlier = np.maximum(np.sort(earlier, axis=1)[:, ::-1] - dstream_S, 0)
    bounds = np.concatenate(
        [hi[:, None], lo[:, None], earlier, np.zeros((len(lo), 1))], axis=1
    )
    uppers, lowers = bounds[:, :-1], bounds[:, 1:]  # node's own first
    p_collisions = p ** np.arange(uppers.shape[1])[None, :]

    result = np.empty((len(ranks), len(alphas)))
    fallback = (lo + hi - 1) / 2
    for k, alpha in enumerate(alphas):
        masses, means = _calc_prior_moments(lowers, uppers, hi[:, None], alpha)
        weights = masses * p_collisions
        total = weights.sum(axis=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            posterior = (weights * means).sum(axis=1) / total
        result[:, k] = np.where(total > 0, posterior, fallback)
    return result


try:
    from numba import prange
except (ImportError, ModuleNotFoundError):  # pragma: no cover
    prange = range


@jit(nopython=True)
def _calc_prior_moment_scalar(
    a: float, b: float, H: float, alpha: float
) -> typing.Tuple[float, float]:
    """Scalar `_calc_prior_moments`, with `H = max(hi, 1)`."""
    if b <= a:
        return 0.0, (a + b - 1) / 2
    u1 = H - b + 1.0
    u2 = H - a + 1.0
    if abs(alpha) < 1e-9:
        mass = u2 - u1
        mean_u = (u1 + u2) / 2
    elif abs(alpha - 1) < 1e-9:
        mass = np.log(u2 / u1)
        mean_u = (u2 - u1) / mass
    elif abs(alpha - 2) < 1e-9:
        mass = 1 / u1 - 1 / u2
        mean_u = np.log(u2 / u1) / mass
    else:
        mass = (u2 ** (1 - alpha) - u1 ** (1 - alpha)) / (1 - alpha)
        moment = (u2 ** (2 - alpha) - u1 ** (2 - alpha)) / (2 - alpha)
        mean_u = moment / mass
    mean = min(max(H + 0.5 - mean_u, a), max(a, b - 1))
    if not np.isfinite(mean):
        mean = (a + b - 1) / 2
    return mass, mean


@jit(nopython=True, parallel=True)
def _calc_means_grid_fast_path(
    retained: np.ndarray,
    ranks: np.ndarray,
    youngest_T: np.ndarray,
    p: float,
    dstream_S: int,
    alphas: np.ndarray,
) -> np.ndarray:
    """Fused, parallel implementation of `_calc_chunk_means_grid`, over
    inner nodes (rows of sorted `retained`) and prior exponents."""
    num_nodes, num_retained = retained.shape
    result = np.empty((num_nodes, len(alphas)))
    for i in prange(num_nodes):
        rank = ranks[i]
        # node's own interval: from node rank to first comparable rank
        # after, or to youngest tip if none
        first_shared = youngest_T[i]
        for j in range(num_retained):
            if rank < retained[i, j] < youngest_T[i]:
                first_shared = retained[i, j]
                break
        lo = max(rank - dstream_S, 0.0)
        hi = max(first_shared - dstream_S, 0.0)
        H = max(hi, 1.0)

        # interval bounds: mismatch bound, node rank, then comparable ranks
        # before node rank, latest first, back to dstream_S
        bounds = np.empty(num_retained + 3)
        bounds[0] = hi
        bounds[1] = lo
        num_bounds = 2
        for j in range(num_retained - 1, -1, -1):
            if retained[i, j] < rank:
                bounds[num_bounds] = max(retained[i, j] - dstream_S, 0.0)
                num_bounds += 1
        bounds[num_bounds] = 0.0
        num_bounds += 1

        for k in range(len(alphas)):
            numerator = 0.0
            denominator = 0.0
            p_collisions = 1.0  # jth interval requires j collisions
            for j in range(num_bounds - 1):
                mass, mean = _calc_prior_moment_scalar(
                    bounds[j + 1], bounds[j], H, alphas[k]
                )
                weight = mass * p_collisions
                numerator += weight * mean
                denominator += weight
                p_collisions *= p
            if denominator > 0:
                result[i, k] = numerator / denominator
            else:
                result[i, k] = (lo + hi - 1) / 2
    return result


class BackwardLagPosterior:
    """Posterior mean divergence times of inner nodes' children, given
    spurious differentia collisions, under a prior with density
    proportional to `u ** -alpha` over backward lag `u = max(hi, 1) - t + 1`
    from each node's mismatch bound `hi`.

    Each inner node's children may truly have diverged within its own
    interval (from its rank to `hi`, the next comparable rank, where they
    differ), or within any earlier interval between comparable ranks, back
    to `dstream_S`, with spurious collisions at each comparable rank in
    between, each with probability `p_differentia_collision`.

    Times are relative to `dstream_S`. Trie must have contiguous ids, be
    topologically sorted, and provide an integer `rank` column, with leaf
    rank `dstream_T - 1`.
    """

    def __init__(
        self: "BackwardLagPosterior",
        trie: pl.DataFrame,
        p_differentia_collision: float,
        dstream_algo: types.ModuleType,
        dstream_S: int,
    ) -> None:
        self._p = p_differentia_collision
        self._dstream_algo = dstream_algo
        self._dstream_S = dstream_S
        self._bounds = (
            None if trie.is_empty() else mark_inner_node_bounds(trie)
        )

    @property
    def is_inner(self: "BackwardLagPosterior") -> np.ndarray:
        """Is each node inner (i.e., were its children compared)?"""
        if self._bounds is None:
            return np.zeros(0, dtype=bool)
        return self._bounds.is_inner

    def inner_means_grid(
        self: "BackwardLagPosterior", alphas: np.ndarray
    ) -> np.ndarray:
        """Posterior mean origin times of inner nodes (rows) for each prior
        exponent in `alphas` (columns), in one pass over comparable ranks."""
        if self._bounds is None:
            return np.zeros((0, len(alphas)), dtype=np.float64)
        ranks, is_inner, compare_T, youngest_T = self._bounds
        inner_ranks = ranks[is_inner].astype(np.float64)
        youngest_T = youngest_T.astype(np.float64)
        result = np.empty((len(compare_T), len(alphas)))
        with log_context_duration("BackwardLagPosterior", logging.info):
            for chunk, retained in iter_retained_ranks(
                self._dstream_algo, self._dstream_S, compare_T
            ):
                result[chunk] = _calc_means_grid_fast_path(
                    retained,
                    inner_ranks[chunk],
                    youngest_T[chunk],
                    float(self._p),
                    int(self._dstream_S),
                    np.asarray(alphas, dtype=np.float64),
                )
        return result

    def with_inner_means(
        self: "BackwardLagPosterior", inner_means: np.ndarray
    ) -> np.ndarray:
        """Origin times for all nodes, given inner nodes' times; leaves and
        unifurcating roots are assigned their rank."""
        if self._bounds is None:
            return np.zeros(0, dtype=np.float64)
        ranks, is_inner, __, __ = self._bounds
        origin_times = (ranks - self._dstream_S).astype(np.float64)
        origin_times[is_inner] = inner_means
        return origin_times

    def origin_times(self: "BackwardLagPosterior", alpha: float) -> np.ndarray:
        """Posterior mean origin times for prior exponent `alpha`, for all
        nodes; leaves and unifurcating roots are assigned their rank."""
        return self.with_inner_means(
            self.inner_means_grid(np.array([alpha]))[:, 0]
        )
