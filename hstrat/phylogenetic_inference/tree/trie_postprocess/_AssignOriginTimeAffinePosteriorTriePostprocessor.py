import functools
import typing
import warnings

import numpy as np
import pandas as pd
from phyloframe import legacy as pfl
import polars as pl

from ...._auxiliary_lib import (
    apply_unique_rows,
    calc_lineage_affine_with_contiguous_ids,
    calc_min_child_value_with_contiguous_ids,
)
from ...priors import UniformPrior
from ...priors._detail import PriorBase
from .._impl import TrieInnerNode
from ._detail import TriePostprocessorBase


def _make_interval_stats(
    prior: PriorBase,
) -> typing.Callable[[int, int], typing.Tuple[float, float]]:
    """Create cached lookup for prior probability mass and conditioned mean
    of interval [begin, end), in rank units offset by `t0`."""

    @functools.lru_cache(maxsize=None)
    def interval_stats(begin: int, end: int) -> typing.Tuple[float, float]:
        begin = max(begin, 0)  # MRCA cannot precede t0
        if end <= begin:
            return 0.0, 0.0
        return (
            float(prior.CalcIntervalProbabilityProxy(begin, end)),
            float(prior.CalcIntervalConditionedMean(begin, end)),
        )

    return interval_stats


def _calc_edge_masses(
    begin_rank: int,
    end_rank: int,
    num_collapsed: int,
    p_differentia_collision: float,
    interval_stats: typing.Callable,
) -> typing.Tuple[float, float]:
    """Sum collision-discounted prior mass (and mass-weighted conditioned
    mean) over intervals between matched ranks along an edge.

    The edge spans `begin_rank` to `end_rank`, with `num_collapsed` matched
    ranks between them that were collapsed away. Collapsed ranks are
    assumed evenly spaced. An MRCA within the j'th interval would require
    spurious differentia collisions at each matched rank thereafter, through
    `end_rank`.
    """
    num_intervals = num_collapsed + 1
    positions = np.round(
        np.linspace(begin_rank, end_rank, num_intervals + 1),
    ).astype(np.int64)
    mass, moment = 0.0, 0.0
    for j in range(num_intervals):
        weight, mean = interval_stats(int(positions[j]), int(positions[j + 1]))
        discount = p_differentia_collision ** (num_intervals - j)
        mass += weight * discount
        moment += weight * mean * discount
    return mass, moment


def _calc_origin_times(
    ftor: "AssignOriginTimeAffinePosteriorTriePostprocessor",
    ancestor_ids: np.ndarray,
    ranks: np.ndarray,  # float, NaN for missing
    num_collapsed: np.ndarray,
    p_differentia_collision: float,
) -> np.ndarray:
    """Implementation detail."""
    interval_stats = _make_interval_stats(ftor._prior)
    p = p_differentia_collision
    n = len(ancestor_ids)
    if n == 0:
        return np.zeros(0, dtype=np.float64)
    is_root = ancestor_ids == np.arange(n)
    is_leaf = ~np.bincount(ancestor_ids[~is_root], minlength=n).astype(bool)
    has_rank = ~np.isnan(ranks)

    # missing ranks (i.e., prefixed roots) treated as t0 boundary
    int_ranks = np.where(has_rank, ranks, 0.0).astype(np.int64)
    ancestor_ranks = int_ranks[ancestor_ids]

    # discounted prior mass contributed by each edge...
    edge_masses, edge_moments = apply_unique_rows(
        lambda begin, end, collapsed: _calc_edge_masses(
            begin, end, collapsed, p, interval_stats
        ),
        ancestor_ranks,
        int_ranks,
        num_collapsed,
    )
    edge_masses[is_root | is_leaf] = 0.0
    edge_moments[is_root | is_leaf] = 0.0

    # ... accumulated along path from root, discounted by collisions needed
    discounts = p ** (num_collapsed.astype(np.float64) + 1.0)
    path_masses = calc_lineage_affine_with_contiguous_ids(
        ancestor_ids, discounts, edge_masses
    )
    path_moments = calc_lineage_affine_with_contiguous_ids(
        ancestor_ids, discounts, edge_moments
    )

    # estimate first rank where children differ (exclusive MRCA bound);
    # for collapsed unifurcations, use first collapsed rank (even spacing);
    # leaf ranks (i.e., dstream_T - 1) also bound MRCA, as leaf origin time
    first_ranks = np.round(
        ancestor_ranks + (int_ranks - ancestor_ranks) / (num_collapsed + 1),
    )
    first_ranks[first_ranks <= ancestor_ranks] = np.inf
    mismatch_ranks = calc_min_child_value_with_contiguous_ids(
        ancestor_ids, first_ranks
    )
    mismatch_ranks = np.where(
        np.isfinite(mismatch_ranks), mismatch_ranks, int_ranks + 1
    ).astype(np.int64)

    # posterior mean, including final interval requiring no collisions
    last_masses, last_means = apply_unique_rows(
        interval_stats, int_ranks, mismatch_ranks
    )
    total_masses = path_masses + last_masses
    with np.errstate(divide="ignore", invalid="ignore"):
        estimates = np.where(
            total_masses > 0,
            (path_moments + last_masses * last_means) / total_masses,
            np.maximum(last_means, int_ranks),
        )

    # bound by children's ranks and ancestors' estimates
    estimates = np.minimum(
        estimates,
        calc_min_child_value_with_contiguous_ids(ancestor_ids, int_ranks),
    )
    estimates = np.where(is_leaf | is_root, int_ranks, estimates)
    estimates = np.where(has_rank, estimates, np.nan)

    # ensure estimates do not precede ancestors' estimates
    lineage_max = (
        pfl.alifestd_mark_lineage_cummax_polars(
            pl.DataFrame(
                {
                    "id": np.arange(n),
                    "ancestor_id": ancestor_ids,
                    "estimate": estimates,
                },
            ),
            "estimate",
            mark_as="lineage_max",
        )
        .get_column("lineage_max")
        .to_numpy()
    )
    return np.where(has_rank, lineage_max, np.nan)


def _call_polars(
    ftor: "AssignOriginTimeAffinePosteriorTriePostprocessor",
    trie: pl.DataFrame,
    p_differentia_collision: float,
) -> pl.DataFrame:
    """Implementation detail."""
    if not pfl.alifestd_has_contiguous_ids_polars(trie):
        raise NotImplementedError("non-contiguous ids not supported")
    if not pfl.alifestd_is_topologically_sorted_polars(trie):
        raise NotImplementedError("non-topologically-sorted not supported")

    schema_names = trie.lazy().collect_schema().names()
    col = ftor._num_collapsed_property
    t0 = (
        pl.col(ftor._t0).cast(pl.Float64).fill_null(0.0)
        if isinstance(ftor._t0, str)
        else pl.lit(float(ftor._t0))
    )
    arrays = (
        trie.lazy()
        .select(
            pl.col("ancestor_id").cast(pl.Int64).alias("ancestor_id"),
            (pl.col("rank").cast(pl.Float64) - t0).alias("rank"),
            (
                pl.col(col).fill_null(0).cast(pl.Int64)
                if col in schema_names
                else pl.lit(0, dtype=pl.Int64)
            ).alias("num_collapsed"),
        )
        .collect()
    )

    origin_times = _calc_origin_times(
        ftor,
        arrays["ancestor_id"].to_numpy(),
        arrays["rank"].fill_null(np.nan).to_numpy(),
        arrays["num_collapsed"].to_numpy(),
        p_differentia_collision,
    )
    return trie.with_columns(
        pl.Series(
            ftor._assigned_property,
            origin_times,
            dtype=pl.Float64,
            nan_to_null=True,
        ),
    )


class AssignOriginTimeAffinePosteriorTriePostprocessor(TriePostprocessorBase):
    """Functor to assign origin time property to trie nodes, correcting for
    bias from spurious differentia collisions.

    Spurious collisions cause lineages to appear to share common ancestry
    for longer than they truly did, so naive estimates of origin times
    (i.e., MRCA generations) are biased toward being too recent. This
    postprocessor instead assigns the posterior mean of each inner node's
    origin time, accounting for all possible collision scenarios.

    Under the provided prior, the MRCA of a node's subtrees is taken to fall
    within any interval between successive matched (i.e., retained in common)
    ranks along the node's path from the root, with posterior weight
    proportional to that interval's prior probability times
    `p_differentia_collision` raised to the number of matched ranks after the
    interval (i.e., the number of spurious collisions that would be
    required). The final interval, between the node's rank and the first
    rank where its children differ, requires no collisions.

    Notes
    -----
    Each inner node is treated as a bifurcation (i.e., one spurious
    collision per matched rank). This assumption holds for binary (single
    bit) differentiae, where at most two children can branch at any rank.
    For wider differentiae, estimates for polytomies may be overcorrected.

    Only polars dataframe tries are supported (e.g., via
    `surface_postprocess_trie` or `surface_build_tree`). Anytree and pandas
    tries raise `NotImplementedError`.

    For collapsed tries (e.g., `surface_postprocess_trie`), the number of
    collapsed-away matched ranks along each edge is read from the
    `hstrat_num_collapsed_unifurcations` column, if present. Collapsed ranks
    are assumed evenly spaced along their edge. Without this column,
    estimates only account for ranks of nodes present in the trie,
    undercorrecting for collision bias.

    Inner node estimates are bounded above by children's ranks and below by
    ancestors' estimates, and leaves are assigned their rank.
    """

    _assigned_property: str  # property name for assigned origin time
    _num_collapsed_property: str  # property name for collapsed counts
    _prior: PriorBase  # prior expectation for ancestor origin times
    _t0: typing.Union[int, str]  # origin time offset, or property name

    def __init__(
        self: "AssignOriginTimeAffinePosteriorTriePostprocessor",
        prior: PriorBase = UniformPrior(),  # ok as kwarg; immutable
        assigned_property: str = "origin_time",
        *,
        num_collapsed_property: str = "hstrat_num_collapsed_unifurcations",
        t0: typing.Union[int, str] = 0,
    ) -> None:
        """Initialize functor instance.

        Parameters
        ----------
        prior : PriorBase, default UniformPrior()
            Prior distribution of ancestor origin times.

            Prior is evaluated over origin times offset by `t0`.
        assigned_property : str, default "origin_time"
            The property name for the assigned origin time.
        num_collapsed_property : str, default "hstrat_num_collapsed_unifurcations"
            The property name for the number of unifurcating nodes collapsed
            away between each node and its ancestor.
        t0 : int or str, default 0
            The property name or constant value for the origin time offset.

            Assigned origin times are relative to `t0`, and origin times
            before `t0` are considered impossible. For
            `surface_postprocess_trie`, use `"dstream_S"`.
        """
        self._assigned_property = assigned_property
        self._num_collapsed_property = num_collapsed_property
        self._prior = prior
        self._t0 = t0

    def __call__(
        self: "AssignOriginTimeAffinePosteriorTriePostprocessor",
        trie: typing.Union[TrieInnerNode, pd.DataFrame, pl.DataFrame],
        p_differentia_collision: float,
        mutate: bool = False,
        progress_wrap: typing.Callable = lambda x: x,
    ) -> typing.Union[TrieInnerNode, pd.DataFrame, pl.DataFrame]:
        """Assign origin times to trie nodes.

        Parameters
        ----------
        trie : pl.DataFrame
            The input trie to be postprocessed.

            Tries must have contiguous ids, be topologically
            sorted, and provide `rank` column.
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
        if isinstance(trie, TrieInnerNode):
            raise NotImplementedError(
                "anytree tries are not supported; "
                "use dataframe tries (e.g., surface_postprocess_trie)",
            )
        elif isinstance(trie, pd.DataFrame):
            raise NotImplementedError(
                "pandas tries are not supported; use polars",
            )
        elif isinstance(trie, pl.DataFrame):
            if p_differentia_collision < 0.5:
                warnings.warn(
                    "AssignOriginTimeAffinePosteriorTriePostprocessor assumes "
                    "bifurcating trie nodes, which holds for binary (single "
                    "bit) differentiae; estimates for polytomies may be "
                    "overcorrected with wider differentiae.",
                )
            if not mutate:
                trie = trie.clone()
            return _call_polars(
                self,
                trie,
                p_differentia_collision,
            )  # no progress wrap
        else:
            raise TypeError  # pragma: no cover
