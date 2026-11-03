"""Posterior divergence times under a power-law prior over backward age,
given spurious differentia collisions, shared by surface postprocessors."""

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


def _integrate_power(
    lower: np.ndarray, upper: np.ndarray, exponent: float
) -> np.ndarray:
    """Integral of v ** exponent from `lower` to `upper` (both > 0)."""
    if exponent == -1:
        return np.log(upper / lower)
    return (upper ** (exponent + 1) - lower ** (exponent + 1)) / (exponent + 1)


def _calc_prior_moments(
    a: np.ndarray, b: np.ndarray, c: np.ndarray, alpha: float
) -> typing.Tuple[np.ndarray, np.ndarray]:
    """Relative prior mass and mean of divergence generation `t` within
    intervals [`a`, `b`), for prior density proportional to `u ** -alpha`
    over backward age `u = c - t` before generation `c`.

    Generations are integrated over unit cells centered on them, i.e., `t`
    over [`a` - 1/2, `b` - 1/2), so that `alpha == 0` gives mass `b - a`
    and mean `(a + b - 1) / 2`. Masses are relative within rows, as backward
    ages are scaled by per-row `c + 1/2`, to avoid overflow.
    """
    scale = c + 0.5
    is_empty = b <= a
    lower = (c - b + 0.5) / scale  # backward age at interval's later end
    upper = np.where(is_empty, lower + 1, c - a + 0.5) / scale
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        mass = _integrate_power(lower, upper, -alpha)
        mean_u = scale * _integrate_power(lower, upper, 1 - alpha) / mass
    mean = c - mean_u
    return (
        np.where(is_empty, 0.0, mass),
        np.where(is_empty | ~np.isfinite(mean), (a + b - 1) / 2, mean),
    )


class _ChunkIntervals(typing.NamedTuple):
    """Candidate divergence intervals for a chunk of inner nodes."""

    uppers: np.ndarray  # interval ends, node's own interval first
    lowers: np.ndarray  # interval starts
    log_p_collisions: np.ndarray  # log-probability of required collisions
    youngest: np.ndarray  # youngest tip generation, per node


def _calc_chunk_intervals(
    retained: np.ndarray,
    ranks: np.ndarray,
    youngest_T: np.ndarray,
    p: float,
    dstream_S: int,
) -> _ChunkIntervals:
    """Candidate divergence intervals, relative to `dstream_S`, for a chunk
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
    youngest = np.maximum(youngest_T - dstream_S, hi)

    # earlier intervals: between successive comparable ranks before node
    # rank, back to dstream_S, latest first; divergence in the jth requires
    # j spurious collisions, at its upper bound and each later comparable
    # rank up to and including node rank
    earlier = np.where(retained < ranks[:, None], retained, -np.inf)
    earlier = np.maximum(np.sort(earlier, axis=1)[:, ::-1] - dstream_S, 0)
    bounds = np.concatenate([hi[:, None], lo[:, None], earlier], axis=1)
    bounds = np.concatenate([bounds, np.zeros((len(lo), 1))], axis=1)
    num_collisions = np.arange(bounds.shape[1] - 1)
    return _ChunkIntervals(
        bounds[:, :-1],
        bounds[:, 1:],
        num_collisions * np.log(p),
        youngest,
    )


class BackwardAgePosterior:
    """Posterior over divergence times of inner nodes' children, given
    spurious differentia collisions, under a prior over divergence
    generation `t` with density proportional to `u ** -alpha`, for backward
    age `u` before the clade's youngest tip.

    Each inner node's children may truly have diverged within its own
    interval (from its rank to the next comparable rank, where they
    differ), or within any earlier interval between comparable ranks, back
    to `dstream_S`, with spurious collisions at each comparable rank in
    between, each with probability `p_differentia_collision`. Divergence
    after the next comparable rank is ruled out, as children would share
    it.

    Times are relative to `dstream_S`. Trie must have contiguous ids, be
    topologically sorted, and provide an integer `rank` column, with leaf
    rank `dstream_T - 1`.
    """

    def __init__(
        self: "BackwardAgePosterior",
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

    def _iter_chunks(
        self: "BackwardAgePosterior",
    ) -> typing.Iterator[typing.Tuple[slice, _ChunkIntervals]]:
        ranks, is_inner, compare_T, youngest_T = self._bounds
        inner_ranks = ranks[is_inner].astype(np.float64)
        youngest_T = youngest_T.astype(np.float64)
        for chunk, retained in iter_retained_ranks(
            self._dstream_algo, self._dstream_S, compare_T
        ):
            yield chunk, _calc_chunk_intervals(
                retained,
                inner_ranks[chunk],
                youngest_T[chunk],
                self._p,
                self._dstream_S,
            )

    @property
    def is_inner(self: "BackwardAgePosterior") -> np.ndarray:
        """Is each node inner (i.e., were its children compared)?"""
        if self._bounds is None:
            return np.zeros(0, dtype=bool)
        return self._bounds.is_inner

    def origin_times(self: "BackwardAgePosterior", alpha: float) -> np.ndarray:
        """Posterior mean origin times, for all nodes; leaves and
        unifurcating roots are assigned their rank."""
        if self._bounds is None:
            return np.zeros(0, dtype=np.float64)
        ranks, is_inner, compare_T, __ = self._bounds
        means = np.empty(len(compare_T))
        with log_context_duration("BackwardAgePosterior", logging.debug):
            for chunk, iv in self._iter_chunks():
                masses, interval_means = _calc_prior_moments(
                    iv.lowers, iv.uppers, iv.youngest[:, None], alpha
                )
                weights = masses * np.exp(iv.log_p_collisions)[None, :]
                total = weights.sum(axis=1)
                fallback = (iv.lowers[:, 0] + iv.uppers[:, 0] - 1) / 2
                with np.errstate(divide="ignore", invalid="ignore"):
                    result = (weights * interval_means).sum(axis=1) / total
                means[chunk] = np.where(total > 0, result, fallback)

        origin_times = (ranks - self._dstream_S).astype(np.float64)
        origin_times[is_inner] = means
        return origin_times

    def log_likelihoods(
        self: "BackwardAgePosterior", alpha: float
    ) -> np.ndarray:
        """Log marginal likelihood of each inner node's observed placement,
        up to a constant not depending on `alpha`.

        Integrates collision probabilities over the prior, normalized over
        all generations from `dstream_S` to the clade's youngest tip.
        """
        if self._bounds is None:
            return np.zeros(0, dtype=np.float64)
        result = np.empty(len(self._bounds.compare_T))
        for chunk, iv in self._iter_chunks():
            youngest = iv.youngest[:, None]
            masses, __ = _calc_prior_moments(
                iv.lowers, iv.uppers, youngest, alpha
            )
            normalizers, __ = _calc_prior_moments(
                np.zeros_like(youngest), youngest, youngest, alpha
            )
            weights = masses * np.exp(iv.log_p_collisions)[None, :]
            with np.errstate(divide="ignore"):
                result[chunk] = np.log(weights.sum(axis=1)) - np.log(
                    normalizers[:, 0]
                )
        return result
