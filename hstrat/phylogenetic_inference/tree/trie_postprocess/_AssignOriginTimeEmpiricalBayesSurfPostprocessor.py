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
from ._detail._comparable_ranks import get_sole_dstream_S, resolve_dstream_algo
from ._detail._exponential_posterior import ExponentialPosterior


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


def _fit_rate(
    posterior: ExponentialPosterior,
    weights: np.ndarray,
    target: float,
    rate_bounds: typing.Tuple[float, float],
    rate_tolerance: float,
) -> float:
    """Bisect prior rate so posterior's weighted mean matches target.

    Posterior means increase with prior rate (higher rates favor more
    recent divergence), so the weighted mean is monotonic.
    """

    def excess(rate: float) -> float:
        return float(np.dot(weights, posterior(rate))) - target

    lo, hi = rate_bounds
    if excess(lo) >= 0:
        warnings.warn(
            f"empirical Bayes target {target} at or below posterior mean "
            f"for lowest prior rate {lo}; clamping to {lo}",
        )
        return lo
    if excess(hi) <= 0:
        warnings.warn(
            f"empirical Bayes target {target} at or above posterior mean "
            f"for highest prior rate {hi}; clamping to {hi}",
        )
        return hi
    while hi - lo > rate_tolerance:
        mid = (lo + hi) / 2
        if excess(mid) < 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _call_polars(
    ftor: "AssignOriginTimeEmpiricalBayesSurfPostprocessor",
    trie: pl.DataFrame,
    p_differentia_collision: float,
) -> pl.DataFrame:
    """Implementation detail."""
    dstream_S = get_sole_dstream_S(trie)
    posterior = ExponentialPosterior(
        trie, p_differentia_collision, ftor._dstream_algo, dstream_S
    )
    pair_counts = _calc_mrca_pair_counts(trie) if len(trie) else np.zeros(0)
    if pair_counts.sum() == 0:  # no leaf pairs to calibrate against
        rate = 0.0
    else:
        weights = pair_counts / pair_counts.sum()
        target = float(
            np.dot(
                weights,
                _calc_geometric_origin_times(
                    trie,
                    p_differentia_collision,
                    ftor._dstream_algo,
                    dstream_S,
                ),
            ),
        )
        rate = _fit_rate(
            posterior,
            weights,
            target,
            ftor._rate_bounds,
            ftor._rate_tolerance,
        )
    logging.info(f" - empirical Bayes prior rate: {rate}")
    return trie.with_columns(
        pl.Series(ftor._assigned_property, posterior(rate), dtype=pl.Float64),
    )


class AssignOriginTimeEmpiricalBayesSurfPostprocessor(TriePostprocessorBase):
    """Functor to assign trie node origin times as posterior means, under a
    prior fit so that their tree-wide average matches the unbiased
    geometric estimate.

    Spurious differentia collisions cause lineages to appear to share
    common ancestry for longer than they truly did. So, a node's children
    may truly have diverged not only within the node's own interval (i.e.,
    between its rank and the next comparable rank, where its children
    differ), but within any earlier interval between comparable ranks, back
    to `dstream_S`. Divergence within the jth interval before the node's own
    requires spurious collisions at j comparable ranks, with probability
    proportional to `p_differentia_collision ** j`.

    Each inner node is assigned its posterior mean divergence time, under a
    prior over generations since `dstream_S`, `t`, with density
    proportional to `exp(rate * t)`. Lower `rate` favors earlier divergence
    (i.e., toward the root), and higher `rate` later divergence (i.e.,
    toward the tips), with `rate = 0` uniform. The prior's tilt within an
    interval depends only on the interval's width, not on how many
    generations have elapsed. The prior rate is fit by empirical Bayes:
    chosen so that the average of node estimates, weighted by the number
    of leaf pairs whose most recent common ancestor each node is, matches
    that of `AssignOriginTimeGeometricSurfPostprocessor`, which is unbiased
    with respect to collisions without assuming a prior. So, the geometric
    estimator sets the tree-wide average, and the posterior distributes it
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
    ...         hstrat.AssignOriginTimeEmpiricalBayesSurfPostprocessor(
    ...             "dstream.steady_algo",
    ...         )
    ...     ),
    ... )
    """

    _assigned_property: str  # property name for assigned origin time
    _dstream_algo: types.ModuleType  # downstream algorithm of surfaces
    _rate_bounds: typing.Tuple[float, float]  # prior rate search range
    _rate_tolerance: float  # prior rate search precision

    def __init__(
        self: "AssignOriginTimeEmpiricalBayesSurfPostprocessor",
        dstream_algo: typing.Union[str, types.ModuleType],
        assigned_property: str = "origin_time",
        *,
        rate_bounds: typing.Tuple[float, float] = (-1.0, 1.0),
        rate_tolerance: float = 1e-6,
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
        rate_bounds : tuple of float, default (-1.0, 1.0)
            Range searched for prior rate, per generation.

            Heuristic: at rates of +/-1 per generation, prior mass within
            intervals spanning more than a few generations concentrates at
            their ends, so posterior means approach their limits. If the fit
            target lies outside the range, the rate is clamped to the nearer
            bound, with a warning.
        rate_tolerance : float, default 1e-6
            Precision to which prior rate is fit, by bisection.
        """
        if not rate_bounds[0] < rate_bounds[1]:
            raise ValueError(f"invalid rate_bounds {rate_bounds}")
        self._dstream_algo = resolve_dstream_algo(dstream_algo)
        self._assigned_property = assigned_property
        self._rate_bounds = tuple(rate_bounds)
        self._rate_tolerance = rate_tolerance

    def __call__(
        self: "AssignOriginTimeEmpiricalBayesSurfPostprocessor",
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
