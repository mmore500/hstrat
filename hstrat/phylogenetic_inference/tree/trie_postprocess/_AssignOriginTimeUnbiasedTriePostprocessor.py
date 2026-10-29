import functools
import typing

import numpy as np
import pandas as pd
from phyloframe import legacy as pfl
import polars as pl

from ...._auxiliary_lib import jit
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


@jit(nopython=True)
def _propagate_path_masses_jit(
    ancestor_ids: np.ndarray,
    edge_masses: np.ndarray,
    edge_moments: np.ndarray,
    discounts: np.ndarray,
) -> typing.Tuple[np.ndarray, np.ndarray]:
    """Accumulate discounted prior mass over path from root, top-down."""
    path_masses = np.zeros(len(ancestor_ids), dtype=np.float64)
    path_moments = np.zeros(len(ancestor_ids), dtype=np.float64)
    for id_, ancestor_id in enumerate(ancestor_ids):
        if ancestor_id == id_:
            continue
        discount = discounts[id_]
        path_masses[id_] = (
            discount * path_masses[ancestor_id] + edge_masses[id_]
        )
        path_moments[id_] = (
            discount * path_moments[ancestor_id] + edge_moments[id_]
        )
    return path_masses, path_moments


@jit(nopython=True)
def _clamp_to_ancestors_jit(
    ancestor_ids: np.ndarray,
    estimates: np.ndarray,
    is_leaf: np.ndarray,
) -> np.ndarray:
    """Ensure inner node estimates do not precede ancestor estimates."""
    for id_, ancestor_id in enumerate(ancestor_ids):
        if ancestor_id == id_ or is_leaf[id_]:
            continue
        if np.isnan(estimates[ancestor_id]):
            continue
        estimates[id_] = max(estimates[id_], estimates[ancestor_id])
    return estimates


def _unique_apply(
    func: typing.Callable, *args: np.ndarray
) -> typing.Tuple[np.ndarray, ...]:
    """Apply func once per unique combination of row-wise args."""
    stacked = np.stack(args, axis=1)
    uniques, inverse = np.unique(stacked, axis=0, return_inverse=True)
    results = np.array(
        [func(*map(int, row)) for row in uniques], dtype=np.float64
    ).reshape(len(uniques), -1)
    return tuple(results[inverse.ravel(), i] for i in range(results.shape[1]))


def _calc_origin_times_numpy(
    ftor: "AssignOriginTimeUnbiasedTriePostprocessor",
    ancestor_ids: np.ndarray,
    ranks: np.ndarray,  # float, NaN for missing
    num_collapsed: np.ndarray,
    p_differentia_collision: float,
) -> np.ndarray:
    """Implementation detail for dataframe postprocessing."""
    interval_stats = _make_interval_stats(ftor._prior)
    p = p_differentia_collision
    n = len(ancestor_ids)
    if n == 0:
        return np.zeros(0, dtype=np.float64)
    ids = np.arange(n)
    is_root = ancestor_ids == ids
    num_children = np.bincount(ancestor_ids[~is_root], minlength=n)
    is_leaf = num_children == 0
    has_rank = ~np.isnan(ranks)

    # missing ranks (i.e., prefixed roots) treated as t0 boundary
    int_ranks = np.where(has_rank, ranks, 0.0).astype(np.int64)

    # discounted prior mass contributed by each edge
    edge_masses, edge_moments = _unique_apply(
        lambda begin, end, collapsed: _calc_edge_masses(
            begin, end, collapsed, p, interval_stats
        ),
        int_ranks[ancestor_ids],
        int_ranks,
        num_collapsed,
    )
    edge_masses[is_root | is_leaf] = 0.0
    edge_moments[is_root | is_leaf] = 0.0
    discounts = p ** (num_collapsed.astype(np.float64) + 1.0)

    path_masses, path_moments = _propagate_path_masses_jit(
        ancestor_ids, edge_masses, edge_moments, discounts
    )

    # estimate first rank where children differ (exclusive MRCA bound);
    # for collapsed unifurcations, use first collapsed rank (even spacing);
    # leaf ranks (i.e., dstream_T - 1) also bound MRCA, as leaf origin time
    first_ranks = np.round(
        int_ranks[ancestor_ids]
        + (int_ranks - int_ranks[ancestor_ids]) / (num_collapsed + 1),
    )
    is_eligible = (first_ranks > int_ranks[ancestor_ids]) & ~is_root
    first_ranks = np.where(is_eligible, first_ranks, np.inf)
    min_first_ranks = np.full(n, np.inf)
    np.minimum.at(
        min_first_ranks, ancestor_ids[~is_root], first_ranks[~is_root]
    )
    mismatch_ranks = np.where(
        np.isfinite(min_first_ranks), min_first_ranks, int_ranks + 1
    ).astype(np.int64)

    (last_masses, last_means) = _unique_apply(
        interval_stats, int_ranks, mismatch_ranks
    )
    total_masses = path_masses + last_masses
    with np.errstate(divide="ignore", invalid="ignore"):
        estimates = np.where(
            total_masses > 0,
            (path_moments + last_masses * last_means) / total_masses,
            np.maximum(last_means, int_ranks),
        )

    # bound by children's ranks
    min_child_ranks = np.full(n, np.inf)
    np.minimum.at(min_child_ranks, ancestor_ids[~is_root], int_ranks[~is_root])
    estimates = np.minimum(estimates, min_child_ranks)

    estimates = np.where(is_leaf | is_root, int_ranks, estimates)
    estimates = np.where(has_rank, estimates, np.nan)
    return _clamp_to_ancestors_jit(ancestor_ids, estimates, is_leaf)


def _get_df_t0(
    ftor: "AssignOriginTimeUnbiasedTriePostprocessor",
    trie: pd.DataFrame,
) -> np.ndarray:
    if isinstance(ftor._t0, str):
        return trie[ftor._t0].to_numpy(dtype=np.float64, na_value=np.nan)
    return np.full(len(trie), ftor._t0, dtype=np.float64)


def _call_pandas(
    ftor: "AssignOriginTimeUnbiasedTriePostprocessor",
    trie: pd.DataFrame,
    p_differentia_collision: float,
) -> pd.DataFrame:
    """Implementation detail."""
    if not pfl.alifestd_has_contiguous_ids(trie):
        raise NotImplementedError("non-contiguous ids not supported")
    if not pfl.alifestd_is_topologically_sorted(trie):
        raise NotImplementedError("non-topologically-sorted not supported")

    ancestor_ids = trie["ancestor_id"].to_numpy(dtype=np.int64)
    t0 = _get_df_t0(ftor, trie)
    ranks = trie["rank"].to_numpy(dtype=np.float64, na_value=np.nan)
    col = ftor._num_collapsed_property
    num_collapsed = (
        trie[col].fillna(0).to_numpy(dtype=np.int64)
        if col in trie.columns
        else np.zeros(len(trie), dtype=np.int64)
    )

    trie[ftor._assigned_property] = _calc_origin_times_numpy(
        ftor,
        ancestor_ids,
        ranks - np.nan_to_num(t0),
        num_collapsed,
        p_differentia_collision,
    )
    return trie


def _call_polars(
    ftor: "AssignOriginTimeUnbiasedTriePostprocessor",
    trie: pl.DataFrame,
    p_differentia_collision: float,
) -> pl.DataFrame:
    """Implementation detail."""
    columns = ["id", "ancestor_id", "rank"]
    for col in (ftor._t0, ftor._num_collapsed_property):
        if isinstance(col, str) and col in trie.columns:
            columns.append(col)
    trie_pd = trie.select(columns).to_pandas()
    trie_pd = _call_pandas(ftor, trie_pd, p_differentia_collision)
    return trie.with_columns(
        pl.Series(
            ftor._assigned_property,
            trie_pd[ftor._assigned_property].to_numpy(),
            dtype=pl.Float64,
            nan_to_null=True,
        ),
    )


class AssignOriginTimeUnbiasedTriePostprocessor(TriePostprocessorBase):
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

    Only dataframe tries are supported (e.g., `surface_postprocess_trie`
    or `surface_build_tree`). Anytree tries raise `NotImplementedError`.

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
        self: "AssignOriginTimeUnbiasedTriePostprocessor",
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
        self: "AssignOriginTimeUnbiasedTriePostprocessor",
        trie: typing.Union[TrieInnerNode, pd.DataFrame, pl.DataFrame],
        p_differentia_collision: float,
        mutate: bool = False,
        progress_wrap: typing.Callable = lambda x: x,
    ) -> typing.Union[TrieInnerNode, pd.DataFrame, pl.DataFrame]:
        """Assign origin times to trie nodes.

        Parameters
        ----------
        trie : pd.DataFrame or pl.DataFrame
            The input trie to be postprocessed.

            Dataframe tries must have contiguous ids, be topologically
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
        pd.DataFrame or pl.DataFrame
            The postprocessed trie with assigned origin times.
        """
        if isinstance(trie, TrieInnerNode):
            raise NotImplementedError(
                "anytree tries are not supported; "
                "use dataframe tries (e.g., surface_postprocess_trie)",
            )
        elif isinstance(trie, pd.DataFrame):
            if not mutate:
                trie = trie.copy()
            return _call_pandas(
                self,
                trie,
                p_differentia_collision,
            )  # no progress wrap
        elif isinstance(trie, pl.DataFrame):
            if not mutate:
                trie = trie.clone()
            return _call_polars(
                self,
                trie,
                p_differentia_collision,
            )  # no progress wrap
        else:
            raise TypeError  # pragma: no cover
