"""Posterior mean divergence times under an exponential prior, given spurious
differentia collisions, shared by surface postprocessors."""

import logging
import types
import typing

import numpy as np
import polars as pl

from ....._auxiliary_lib import log_context_duration
from ._comparable_ranks import (
    first_retained_between,
    iter_retained_ranks,
    mark_inner_node_bounds,
)


def _calc_exponential_prior_moments(
    a: np.ndarray, b: np.ndarray, shift: np.ndarray, rate: float
) -> typing.Tuple[np.ndarray, np.ndarray]:
    """Relative prior mass and conditional mean of divergence generation `t`
    within intervals [`a`, `b`), for prior density proportional to
    `exp(rate * t)`.

    Masses are relative within rows, scaled by `exp(-shift)` per row to
    avoid overflow. Means are of continuous `t`, shifted by -1/2 to match
    discrete generations' midpoints, so that `rate == 0` gives `b - a` and
    `(a + b - 1) / 2`.
    """
    width = np.maximum(b - a, 0)
    d = rate * width
    is_small = np.abs(d) < 1e-6
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        # mass: integral of exp(rate * t - shift) over [a, b)
        mass = np.where(
            is_small,
            width * np.exp(rate * a - shift) * (1 + d / 2),
            (np.exp(rate * b - shift) - np.exp(rate * a - shift)) / rate,
        )
        # conditional mean: a + width * (1 / (1 - exp(-d)) - 1 / d)
        fraction = np.where(is_small, 0.5 + d / 12, 1 / -np.expm1(-d) - 1 / d)
    mean = a + width * fraction - 0.5
    is_empty = width <= 0
    return (
        np.where(is_empty, 0.0, mass),
        np.where(is_empty | ~np.isfinite(mean), (a + b - 1) / 2, mean),
    )


def _calc_posterior_means_chunk(
    retained: np.ndarray,
    ranks: np.ndarray,
    youngest_T: np.ndarray,
    p: float,
    dstream_S: int,
    rate: float,
) -> np.ndarray:
    """Posterior mean divergence times, relative to `dstream_S`, for a chunk
    of inner nodes, given sorted ranks `retained` at their comparison
    `dstream_T`."""
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
    bounds = np.concatenate([hi[:, None], lo[:, None], earlier], axis=1)
    bounds = np.concatenate([bounds, np.zeros((len(lo), 1))], axis=1)
    uppers, lowers = bounds[:, :-1], bounds[:, 1:]  # node's own first
    num_collisions = np.arange(uppers.shape[1])

    # largest exponent in each row, so relative masses don't overflow
    shift = np.where(rate > 0, rate * hi, 0.0)[:, None]
    masses, means = _calc_exponential_prior_moments(
        lowers, uppers, shift, rate
    )
    weights = masses * p ** num_collisions[None, :]
    total = weights.sum(axis=1)
    fallback = (lo + hi - 1) / 2
    with np.errstate(divide="ignore", invalid="ignore"):
        result = (weights * means).sum(axis=1) / total
    return np.where(total > 0, result, fallback)


class ExponentialPosterior:
    """Calculates posterior mean origin times, relative to `dstream_S`, for
    prior density over divergence generations since `dstream_S`
    proportional to `exp(rate * t)`.

    Each inner node's children may truly have diverged within its own
    interval (from its rank to the next comparable rank, where they
    differ), or within any earlier interval between comparable ranks, back
    to `dstream_S`, with spurious collisions at each comparable rank in
    between, each with probability `p_differentia_collision`.

    Trie must have contiguous ids, be topologically sorted, and provide an
    integer `rank` column, with leaf rank `dstream_T - 1`. Leaves and
    unifurcating roots are assigned their rank.
    """

    def __init__(
        self: "ExponentialPosterior",
        trie: pl.DataFrame,
        p_differentia_collision: float,
        dstream_algo: types.ModuleType,
        dstream_S: int,
    ) -> None:
        self._p = p_differentia_collision
        self._dstream_algo = dstream_algo
        self._dstream_S = dstream_S
        if trie.is_empty():
            self._bounds = None
            return
        self._bounds = mark_inner_node_bounds(trie)

    def __call__(self: "ExponentialPosterior", rate: float) -> np.ndarray:
        """Posterior mean origin times for prior rate `rate`."""
        if self._bounds is None:
            return np.zeros(0, dtype=np.float64)
        ranks, is_inner, compare_T, youngest_T = self._bounds
        inner_ranks = ranks[is_inner].astype(np.float64)
        youngest_T = youngest_T.astype(np.float64)

        posterior_means = np.empty(len(compare_T))
        with log_context_duration("_calc_posterior_means", logging.debug):
            for chunk, retained in iter_retained_ranks(
                self._dstream_algo, self._dstream_S, compare_T
            ):
                posterior_means[chunk] = _calc_posterior_means_chunk(
                    retained,
                    inner_ranks[chunk],
                    youngest_T[chunk],
                    self._p,
                    self._dstream_S,
                    rate,
                )

        origin_times = (ranks - self._dstream_S).astype(np.float64)
        origin_times[is_inner] = posterior_means
        return origin_times
