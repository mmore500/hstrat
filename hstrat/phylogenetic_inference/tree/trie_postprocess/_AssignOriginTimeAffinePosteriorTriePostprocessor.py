import typing
import warnings

import numpy as np
import pandas as pd
from phyloframe import legacy as pfl
import polars as pl

from ...._auxiliary_lib import jit
from ...priors import UniformPrior
from ...priors._detail import PriorBase
from .._impl import TrieInnerNode
from ._detail import TriePostprocessorBase


@jit(nopython=True)
def _calc_interval_stats(
    begin: float, end: float
) -> typing.Tuple[float, float]:
    """Calculate uniform prior mass, and mass times conditioned mean, of
    interval [begin, end), in rank units offset by `t0`."""
    # MRCA cannot precede t0
    begin, end = max(begin, 0.0), max(end, 0.0)
    mass = end - begin
    return mass, mass * (begin + end - 1) / 2


@jit(nopython=True)
def _calc_edge_masses_fast_path(
    begin_ranks: np.ndarray,
    end_ranks: np.ndarray,
    num_collapsed: np.ndarray,
    p_differentia_collision: float,
) -> typing.Tuple[np.ndarray, np.ndarray]:
    """Sum collision-discounted uniform prior mass (and its first moment)
    over intervals between matched ranks along each edge.

    Each edge spans `begin_ranks` to `end_ranks`, with `num_collapsed`
    matched ranks between them that were collapsed away. Collapsed ranks are
    assumed evenly spaced. An MRCA within the j'th interval would require
    spurious differentia collisions at each matched rank thereafter, through
    the edge's end rank.
    """
    masses = np.zeros(len(begin_ranks), dtype=np.float64)
    moments = np.zeros(len(begin_ranks), dtype=np.float64)
    for k, begin_rank in enumerate(begin_ranks):
        num_intervals = num_collapsed[k] + 1
        span = end_ranks[k] - begin_rank
        begin = float(begin_rank)
        for j in range(num_intervals):
            end = np.rint(begin_rank + span * (j + 1) / num_intervals)
            # collapsed ranks are distinct, except where preceding t0
            assert begin < end or end <= 0
            mass, moment = _calc_interval_stats(begin, end)
            discount = p_differentia_collision ** (num_intervals - j)
            masses[k] += mass * discount
            moments[k] += moment * discount
            begin = end
    return masses, moments


def _calc_origin_times(
    ancestor_ids: np.ndarray,
    ranks: np.ndarray,  # int, offset by t0
    num_collapsed: np.ndarray,
    p_differentia_collision: float,
) -> np.ndarray:
    """Implementation detail."""
    p = p_differentia_collision
    n = len(ancestor_ids)
    if n == 0:
        return np.zeros(0, dtype=np.float64)
    is_root = ancestor_ids == np.arange(n)
    is_leaf = ~np.bincount(ancestor_ids[~is_root], minlength=n).astype(bool)
    is_inner = ~(is_root | is_leaf)

    ancestor_ranks = ranks[ancestor_ids]

    # discounted prior mass contributed by each edge...
    edge_masses = np.zeros(n, dtype=np.float64)
    edge_moments = np.zeros(n, dtype=np.float64)
    (
        edge_masses[is_inner],
        edge_moments[is_inner],
    ) = _calc_edge_masses_fast_path(
        ancestor_ranks[is_inner],
        ranks[is_inner],
        num_collapsed[is_inner],
        p,
    )

    # ... accumulated along path from root, discounted by collisions needed
    tree = pl.DataFrame({"id": np.arange(n), "ancestor_id": ancestor_ids})
    discounts = p ** (num_collapsed.astype(np.float64) + 1.0)
    path_masses, path_moments = (
        pfl.alifestd_mark_to_array_polars(
            tree.with_columns(
                _scale=pl.Series(discounts),
                _offset=pl.Series(edge_values),
            ),
            pfl.alifestd_mark_lineage_affine_polars,
            scale="_scale",
            offset="_offset",
        )
        for edge_values in (edge_masses, edge_moments)
    )

    # estimate first rank where children differ (exclusive MRCA bound);
    # for collapsed unifurcations, use first collapsed rank (even spacing);
    # leaf ranks (i.e., dstream_T - 1) also bound MRCA, as leaf origin time
    first_ranks = np.round(
        ancestor_ranks + (ranks - ancestor_ranks) / (num_collapsed + 1),
    )
    first_ranks[first_ranks <= ancestor_ranks] = np.inf
    mismatch_ranks = pfl.alifestd_mark_to_array_polars(
        tree.with_columns(_values=pl.Series(first_ranks)),
        pfl.alifestd_mark_min_child_value_polars,
        values="_values",
    )
    mismatch_ranks = np.where(
        np.isfinite(mismatch_ranks) & ~is_leaf, mismatch_ranks, ranks + 1
    ).astype(np.int64)
    assert (mismatch_ranks > ranks).all()

    # posterior mean, including final interval requiring no collisions
    # MRCA cannot precede t0
    clamped_ranks = np.maximum(ranks, 0)
    clamped_mismatch_ranks = np.maximum(mismatch_ranks, 0)
    last_masses = clamped_mismatch_ranks - clamped_ranks
    last_moments = (
        last_masses * (clamped_ranks + clamped_mismatch_ranks - 1) / 2
    )
    total_masses = path_masses + last_masses
    with np.errstate(divide="ignore", invalid="ignore"):
        estimates = np.where(
            total_masses > 0,
            (path_moments + last_moments) / total_masses,
            clamped_ranks,  # all candidate intervals precede t0
        )

    # inner node MRCA precedes its children; roots and leaves keep own rank
    min_child_ranks = pfl.alifestd_mark_to_array_polars(
        tree.with_columns(_values=pl.Series(ranks)),
        pfl.alifestd_mark_min_child_value_polars,
        values="_values",
    )
    estimates = np.where(
        is_inner,
        np.minimum(estimates, min_child_ranks),
        ranks,
    )

    # each node's posterior is its parent's (rescaled), plus mass only at
    # later ranks, so estimates cannot precede ancestors' estimates
    assert (estimates >= estimates[ancestor_ids] - 1e-6).all()

    return estimates


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
    col = "hstrat_collapsed_unifurcations"
    t0 = (
        pl.col(ftor._t0).cast(pl.Int64)
        if isinstance(ftor._t0, str)
        else pl.lit(ftor._t0, dtype=pl.Int64)
    )
    arrays = (
        trie.lazy()
        .select(
            pl.col("ancestor_id").cast(pl.Int64).alias("ancestor_id"),
            (pl.col("rank").cast(pl.Int64) - t0).alias("rank"),
            (
                pl.col(col).cast(pl.Int64)
                if col in schema_names
                else pl.lit(0, dtype=pl.Int64)
            ).alias("num_collapsed"),
        )
        .collect()
    )
    assert arrays["rank"].null_count() == 0
    assert arrays["num_collapsed"].null_count() == 0

    origin_times = _calc_origin_times(
        arrays["ancestor_id"].to_numpy(),
        arrays["rank"].to_numpy(),
        arrays["num_collapsed"].to_numpy(),
        p_differentia_collision,
    )
    return trie.with_columns(
        pl.Series(
            ftor._assigned_property,
            origin_times,
            dtype=pl.Float64,
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

    Under a uniform prior, the MRCA of a node's subtrees is taken to fall
    within any interval between successive matched (i.e., retained in common)
    ranks along the node's path from the root, with posterior weight
    proportional to that interval's prior probability times
    `p_differentia_collision` raised to the number of matched ranks after the
    interval (i.e., the number of spurious collisions that would be
    required). The final interval, between the node's rank and the first
    rank where its children differ, requires no collisions.

    Notes
    -----
    Only `UniformPrior` is currently supported.

    Each inner node is treated as a bifurcation (i.e., one spurious
    collision per matched rank). This assumption holds for binary (single
    bit) differentiae, where at most two children can branch at any rank.
    For wider differentiae, estimates for polytomies may be overcorrected.

    Only polars dataframe tries are supported (e.g., via
    `surface_postprocess_trie` or `surface_build_tree`). Anytree and pandas
    tries raise `NotImplementedError`.

    For collapsed tries (e.g., `surface_postprocess_trie`), the number of
    collapsed-away matched ranks along each edge is read from the
    `hstrat_collapsed_unifurcations` column, if present. Collapsed ranks
    are assumed evenly spaced along their edge. Without this column,
    estimates only account for ranks of nodes present in the trie,
    undercorrecting for collision bias.

    Inner node estimates are bounded above by children's ranks and below by
    ancestors' estimates, and leaves are assigned their rank.
    """

    _assigned_property: str  # property name for assigned origin time
    _t0: typing.Union[int, str]  # origin time offset, or property name

    def __init__(
        self: "AssignOriginTimeAffinePosteriorTriePostprocessor",
        prior: PriorBase = UniformPrior(),  # ok as kwarg; immutable
        assigned_property: str = "origin_time",
        *,
        t0: typing.Union[int, str] = 0,
    ) -> None:
        """Initialize functor instance.

        Parameters
        ----------
        prior : PriorBase, default UniformPrior()
            Prior distribution of ancestor origin times.

            Prior is evaluated over origin times offset by `t0`. Only
            `UniformPrior` is currently supported.
        assigned_property : str, default "origin_time"
            The property name for the assigned origin time.
        t0 : int or str, default 0
            The property name or constant value for the origin time offset.

            Assigned origin times are relative to `t0`, and origin times
            before `t0` are considered impossible. For
            `surface_postprocess_trie`, use `"dstream_S"`.
        """
        if not isinstance(prior, UniformPrior):
            raise NotImplementedError("only UniformPrior is supported")
        self._assigned_property = assigned_property
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
