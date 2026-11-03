import logging
import types
import typing
import warnings

import numpy as np
from phyloframe import legacy as pfl
import polars as pl

from ._AssignOriginTimeGeometricSurfPostprocessor import (
    _calc_geometric_origin_times,
)
from ._detail import TriePostprocessorBase
from ._detail._backward_lag_posterior import BackwardLagPosterior
from ._detail._comparable_ranks import get_sole_dstream_S, resolve_dstream_algo


def _calc_mrca_pair_counts(trie: pl.DataFrame) -> np.ndarray:
    """Number of leaf pairs whose most recent common ancestor is each node.

    Trie must have contiguous ids and be topologically sorted.
    """
    tree = trie.select(pl.col("id", "ancestor_id").cast(pl.Int64))
    num_leaves = pfl.alifestd_mark_to_array_polars(
        tree, pfl.alifestd_mark_num_leaves_polars
    ).astype(np.float64)
    ids = tree["id"].to_numpy()
    ancestors = tree["ancestor_id"].to_numpy()
    is_child = ids != ancestors
    child_sq_sums = np.zeros(len(ids))
    np.add.at(child_sq_sums, ancestors[is_child], num_leaves[is_child] ** 2)
    has_children = np.bincount(ancestors[is_child], minlength=len(ids)) > 0
    return np.where(has_children, (num_leaves**2 - child_sq_sums) / 2, 0.0)


def _benchmark(
    grid_means: np.ndarray,
    weights: np.ndarray,
    target: float,
    alpha_grid: np.ndarray,
) -> typing.Tuple[np.ndarray, float]:
    """Interpolate inner nodes' posterior means between prior exponents
    bracketing where their weighted mean matches target.

    Posterior means increase with prior exponent, so the weighted mean is
    monotonic over grid columns. Returns interpolated means and the
    corresponding interpolated prior exponent.
    """
    grid_sums = weights @ grid_means
    for end, beyond in (
        (0, target <= grid_sums[0]),
        (-1, target >= grid_sums[-1]),
    ):
        if beyond:
            warnings.warn(
                f"benchmarking target {target} outside range attainable "
                f"over alpha_grid; clamping prior exponent to {alpha_grid[end]}",
            )
            return grid_means[:, end], float(alpha_grid[end])
    k = int(np.searchsorted(grid_sums, target)) - 1
    lam = (target - grid_sums[k]) / (grid_sums[k + 1] - grid_sums[k])
    return (
        (1 - lam) * grid_means[:, k] + lam * grid_means[:, k + 1],
        float((1 - lam) * alpha_grid[k] + lam * alpha_grid[k + 1]),
    )


def _call_polars(
    ftor: "AssignOriginTimeBenchmarkedBayesSurfPostprocessor",
    trie: pl.DataFrame,
    p_differentia_collision: float,
) -> pl.DataFrame:
    """Implementation detail."""
    dstream_S = get_sole_dstream_S(trie)
    posterior = BackwardLagPosterior(
        trie, p_differentia_collision, ftor._dstream_algo, dstream_S
    )
    if not posterior.is_inner.any():  # nothing to benchmark
        origin_times = posterior.origin_times(0.0)
    else:
        pair_counts = _calc_mrca_pair_counts(trie)
        weights = (pair_counts / pair_counts.sum())[posterior.is_inner]
        geometric = _calc_geometric_origin_times(
            trie, p_differentia_collision, ftor._dstream_algo, dstream_S
        )[posterior.is_inner]
        inner_means, alpha = _benchmark(
            posterior.inner_means_grid(ftor._alpha_grid),
            weights,
            float(np.dot(weights, geometric)),
            ftor._alpha_grid,
        )
        logging.info(f" - benchmarked Bayes prior exponent: {alpha}")
        origin_times = posterior.with_inner_means(inner_means)
    return trie.with_columns(
        pl.Series(ftor._assigned_property, origin_times, dtype=pl.Float64),
    )


class AssignOriginTimeBenchmarkedBayesSurfPostprocessor(TriePostprocessorBase):
    """Functor to assign trie node origin times as posterior means, under a
    prior benchmarked so that their tree-wide average matches the
    collision-unbiased geometric estimate (i.e., benchmarked Bayes).

    Spurious differentia collisions cause lineages to appear to share
    common ancestry for longer than they truly did. So, a node's children
    may truly have diverged not only within the node's own interval (i.e.,
    between its rank and its mismatch bound `hi`, the next comparable rank,
    where its children differ), but within any earlier interval between
    comparable ranks, back to `dstream_S`. Divergence within the jth
    interval before the node's own requires spurious collisions at j
    comparable ranks, with probability proportional to
    `p_differentia_collision ** j`.

    Each inner node is assigned its posterior mean divergence time `t`,
    under a power-law prior over backward lag from its mismatch bound,
    `u = max(hi, 1) - t + 1`, with density proportional to `u ** -alpha`.
    So, `u = 1` at the top of every node's own interval, whether its
    descendants were sampled long or soon after. With `alpha = 0`, the prior
    is uniform over generations. Higher `alpha` concentrates weight near the
    mismatch bound (i.e., more recent divergence), and lower `alpha` toward
    deeper intervals.

    A single tree-wide `alpha` is benchmarked (i.e., as in Bayesian
    benchmarking; Datta, Ghosh, et al. 2011), so that the average of node
    estimates, weighted by the number
    of leaf pairs whose most recent common ancestor each node is, matches
    that of `AssignOriginTimeGeometricSurfPostprocessor`, which is unbiased
    with respect to collisions without assuming a prior. Posterior means are
    evaluated over `alpha_grid` and linearly interpolated between the grid
    exponents bracketing the target. So, the geometric estimator sets the
    tree-wide average over leaf pairs, and the posterior distributes it
    across nodes, with each estimate bounded within its own and earlier
    intervals.

    Comparable ranks are looked up as for
    `AssignOriginTimeGeometricSurfPostprocessor`: from `dstream_algo`, as
    the ranks retained at the largest of the node's children's minimum tip
    `dstream_T`, truncated at the clade's minimum tip `dstream_T`.

    Notes
    -----
    Each node is estimated independently, so chronological consistency
    between nodes is not guaranteed.

    Only polars dataframe tries with a uniform `dstream_S` are supported
    (e.g., via `surface_postprocess_trie`). Origin times are relative to
    `dstream_S`. Leaf ranks are taken to be `dstream_T - 1`. Leaves and
    unifurcating roots are assigned their rank.

    Examples
    --------
    >>> hstrat.dataframe.surface_build_tree(  # doctest: +SKIP
    ...     df,
    ...     trie_postprocessor=(
    ...         hstrat.AssignOriginTimeBenchmarkedBayesSurfPostprocessor(
    ...             "dstream.steady_algo",
    ...         )
    ...     ),
    ... )
    """

    _assigned_property: str  # property name for assigned origin time
    _dstream_algo: types.ModuleType  # downstream algorithm of surfaces
    _alpha_grid: np.ndarray  # prior exponents evaluated

    def __init__(
        self: "AssignOriginTimeBenchmarkedBayesSurfPostprocessor",
        dstream_algo: typing.Union[str, types.ModuleType],
        assigned_property: str = "origin_time",
        *,
        alpha_grid: typing.Sequence[float] = tuple(np.linspace(-3, 3, 25)),
    ) -> None:
        """Initialize functor instance.

        Parameters
        ----------
        dstream_algo : str or module
            Downstream algorithm used to curate surfaces, used to look up
            retained ranks.

            For example, `"dstream.steady_algo"` or `dstream.steady_algo`.
        assigned_property : str, default "origin_time"
            Property name for assigned origin time.
        alpha_grid : sequence of float, default 25 values from -3 to 3
            Prior exponents `alpha` evaluated, in increasing order.

            Heuristic. If the benchmarking target lies beyond the range
            attainable over the grid, estimates are clamped to the nearer
            end of the grid, with a warning.
        """
        alpha_grid = np.asarray(alpha_grid, dtype=np.float64)
        if len(alpha_grid) < 2 or not (np.diff(alpha_grid) > 0).all():
            raise ValueError("alpha_grid must be increasing, of length >= 2")
        self._dstream_algo = resolve_dstream_algo(dstream_algo)
        self._assigned_property = assigned_property
        self._alpha_grid = alpha_grid

    def __call__(
        self: "AssignOriginTimeBenchmarkedBayesSurfPostprocessor",
        trie: pl.DataFrame,
        p_differentia_collision: float,
        mutate: bool = False,
        progress_wrap: typing.Callable = lambda x: x,
    ) -> pl.DataFrame:
        """Assign origin times to trie nodes.

        Parameters
        ----------
        trie : pl.DataFrame
            The input trie to be postprocessed.

            Only polars dataframe tries are supported; other types raise
            `NotImplementedError`. Tries must have contiguous ids, be
            topologically sorted, and provide `rank` and `dstream_S`
            columns.
        p_differentia_collision : float
            Probability of a randomly-generated differentia matching an
            existing differentia.
        mutate : bool, default False
            Are side effects on the input argument `trie` allowed?
        progress_wrap : typing.Callable, optional
            Pass tqdm or equivalent to report progress.

            Not used in the current implementation.

        Returns
        -------
        pl.DataFrame
            The postprocessed trie with assigned origin times.
        """
        if not isinstance(trie, pl.DataFrame):
            raise NotImplementedError(
                f"{type(trie)} tries are not supported; use polars "
                "dataframe tries (e.g., surface_postprocess_trie)",
            )
        if not mutate:
            trie = trie.clone()
        return _call_polars(self, trie, p_differentia_collision)
