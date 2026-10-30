import types
import typing

from downstream import dstream
import numpy as np
import pandas as pd
from phyloframe import legacy as pfl
import polars as pl

from .._impl import TrieInnerNode
from ._detail import TriePostprocessorBase


def _resolve_dstream_algo(
    dstream_algo: typing.Union[str, types.ModuleType],
) -> types.ModuleType:
    """Look up downstream algorithm module by name, if needed."""
    if isinstance(dstream_algo, str):
        return getattr(dstream, dstream_algo.removeprefix("dstream."))
    return dstream_algo


def _lookup_retained_ranks(
    dstream_algo: types.ModuleType, S: int, T: np.ndarray
) -> typing.Tuple[np.ndarray, np.ndarray]:
    """Look up sorted retained ranks for each distinct `T`, plus index
    mapping each `T` to its row."""
    unique_T, inverse = np.unique(T, return_inverse=True)
    retained = dstream_algo.lookup_ingest_times_batched(
        S, unique_T.astype(np.uint64), parallel=False
    ).astype(np.float64)
    # pad with inf, for lookups past most recent retained rank
    retained = np.concatenate(
        [retained, np.full((len(unique_T), 1), np.inf)], axis=1
    )
    return np.sort(retained, axis=1), inverse


def _calc_next_retained(
    retained: np.ndarray, inverse: np.ndarray, after: np.ndarray
) -> np.ndarray:
    """First retained rank strictly after `after`, per row (inf if none)."""
    rows = retained[inverse]
    j = np.minimum((rows <= after[:, None]).sum(axis=1), rows.shape[1] - 1)
    return rows[np.arange(len(rows)), j]


def _calc_next_shared(
    retained: np.ndarray,
    inverse: np.ndarray,
    parent_ids: np.ndarray,
    after: np.ndarray,
    num_nodes: int,
) -> np.ndarray:
    """First rank strictly after `after[parent]` retained by every child's
    youngest tip, per parent node (inf if none).

    Leapfrogs: takes max over children of their next retained rank, then
    repeats from that candidate (inclusive) until candidates stabilize.
    """

    def max_over_children(child_next: np.ndarray) -> np.ndarray:
        result = np.full(num_nodes, -np.inf)
        np.maximum.at(result, parent_ids, child_next)
        return np.where(np.isfinite(after), result, np.inf)

    candidate = max_over_children(
        _calc_next_retained(retained, inverse, after[parent_ids]),
    )
    while True:
        at_or_after = np.nextafter(candidate[parent_ids], -np.inf)
        updated = max_over_children(
            _calc_next_retained(retained, inverse, at_or_after),
        )
        if np.array_equal(updated, candidate):
            return candidate
        candidate = updated


def _calc_origin_times(
    ancestor_ids: np.ndarray,
    ranks: np.ndarray,  # int, raw (not offset by t0)
    t0s: np.ndarray,  # int
    p_differentia_collision: float,
    dstream_algo: types.ModuleType,
    dstream_S: int,
) -> np.ndarray:
    """Implementation detail."""
    p = p_differentia_collision
    n = len(ancestor_ids)
    if n == 0:
        return np.zeros(0, dtype=np.float64)

    ids = np.arange(n)
    is_root = ancestor_ids == ids
    num_children = np.bincount(ancestor_ids[~is_root], minlength=n)
    is_leaf = num_children == 0
    # roots with multiple children bound divergence like inner nodes
    is_inner = ~is_leaf & (~is_root | (num_children >= 2))

    # youngest (minimum dstream_T) tip within each node's clade
    tip_Ts = np.where(is_leaf, ranks + 1, np.nan)  # leaf rank is T - 1
    youngest_Ts = pfl.alifestd_mark_to_array_polars(
        pl.DataFrame(
            {
                "id": ids,
                "ancestor_id": ancestor_ids,
                "_values": pl.Series(tip_Ts, nan_to_null=True),
            },
        ),
        pfl.alifestd_mark_lineage_cummin_polars,
        values="_values",
        reverse=True,
    ).astype(np.int64)

    # retained ranks of each child's youngest tip are its comparable ranks
    child_ids = ids[~is_root]
    parent_ids = ancestor_ids[child_ids]
    retained, inverse = _lookup_retained_ranks(
        dstream_algo, dstream_S, youngest_Ts[child_ids]
    )

    # mismatch rank: first rank after node shared by all children; and
    # following shared rank, bounding the next interval
    after = np.where(is_inner, ranks, np.inf).astype(np.float64)
    first_shared = _calc_next_shared(retained, inverse, parent_ids, after, n)
    second_shared = _calc_next_shared(
        retained,
        inverse,
        parent_ids,
        first_shared,
        n,
    )

    # intervals end at youngest tip if no further shared rank
    youngest_Ts = youngest_Ts.astype(np.float64)
    is_terminal = ~np.isfinite(first_shared)
    first_shared = np.where(is_terminal, youngest_Ts, first_shared)
    second_shared = np.where(
        np.isfinite(second_shared), second_shared, youngest_Ts
    )

    # midpoints of node's interval and the next, offset by t0;
    # MRCA cannot precede t0
    lo = np.maximum(ranks - t0s, 0)
    mid = np.maximum(first_shared - t0s, 0)
    hi = np.maximum(second_shared - t0s, 0)
    this_midpoints = (lo + mid - 1) / 2
    next_midpoints = (mid + hi - 1) / 2

    # spurious collisions at successive shared ranks are geometric, so
    # extrapolating back from next interval cancels expected inflation;
    # no extrapolation if no shared rank remains to collide at
    estimates = np.where(
        is_terminal,
        this_midpoints,
        (this_midpoints - p * next_midpoints) / (1 - p),
    )
    return np.where(is_inner, estimates, ranks - t0s).astype(np.float64)


def _call_polars(
    ftor: "AssignOriginTimeGeometricTriePostprocessor",
    trie: pl.DataFrame,
    p_differentia_collision: float,
) -> pl.DataFrame:
    """Implementation detail."""
    if not pfl.alifestd_has_contiguous_ids_polars(trie):
        raise NotImplementedError("non-contiguous ids not supported")
    if not pfl.alifestd_is_topologically_sorted_polars(trie):
        raise NotImplementedError("non-topologically-sorted not supported")

    dstream_S = (
        trie.lazy().select(pl.col("dstream_S").unique()).collect().to_series()
    )
    assert len(dstream_S) <= 1, "mixed dstream_S not supported"

    t0 = (
        pl.col(ftor._t0).cast(pl.Int64)
        if isinstance(ftor._t0, str)
        else pl.lit(ftor._t0, dtype=pl.Int64)
    )
    arrays = (
        trie.lazy()
        .select(
            pl.col("ancestor_id").cast(pl.Int64).alias("ancestor_id"),
            pl.col("rank").cast(pl.Int64).alias("rank"),
            t0.alias("t0"),
        )
        .collect()
    )
    assert arrays["rank"].null_count() == 0

    origin_times = _calc_origin_times(
        arrays["ancestor_id"].to_numpy(),
        arrays["rank"].to_numpy(),
        arrays["t0"].to_numpy(),
        p_differentia_collision,
        ftor._dstream_algo,
        int(dstream_S.item()) if len(dstream_S) else 0,
    )
    return trie.with_columns(
        pl.Series(ftor._assigned_property, origin_times, dtype=pl.Float64),
    )


class AssignOriginTimeGeometricTriePostprocessor(TriePostprocessorBase):
    """Functor to assign origin time property to trie nodes, unbiased
    with respect to spurious differentia collisions.

    Spurious collisions cause lineages to appear to share common ancestry
    for longer than they truly did, so naive estimates of origin times
    (i.e., MRCA generations) are biased toward being too recent. This
    postprocessor corrects for that bias without assuming a prior.

    For a pair of lineages that truly diverged within some interval between
    shared retained ranks, the number of subsequent shared ranks with
    spurious collisions is geometrically distributed, regardless of where
    the divergence falls or which ranks are retained. Each inner node is
    assigned

        (c0 - p * c1) / (1 - p),

    where c0 is the midpoint of the interval between the node's rank and
    the next rank shared by its children (i.e., where they differ), c1 is
    the midpoint of the following shared interval, and p is
    `p_differentia_collision`. This choice makes estimates' expected value,
    over collision outcomes, equal the collision-free interval midpoint for
    every true divergence time. Where no shared rank remains between a
    node and its tips, the interval midpoint is assigned as-is.

    Shared ranks are looked up from `dstream_algo` using the youngest (i.e.,
    minimum `dstream_T`) tip under each child, so they need not be stored
    in the trie.

    Notes
    -----
    Estimates are unbiased on average, not individually: they may precede
    ancestors' estimates or children's ranks. Use another postprocessor if
    best per-node estimates or chronological consistency are needed.

    Estimates target divergence times between lineages under different
    children, so they correspond to clade MRCA times where reconstructed
    topology is correct.

    Lineages that diverged before their first shared rank appear under
    separate roots, with no common ancestor in the trie. To estimate their
    divergence times, join roots under a single global root at rank
    `dstream_S`
    beforehand. Roots with multiple children are estimated like inner
    nodes, so this global root is assigned the same unbiased estimate.

    Only polars dataframe tries with a uniform `dstream_S` are supported
    (e.g., via `surface_postprocess_trie`). Leaf ranks are taken to be
    `dstream_T - 1`. Leaves and unifurcating roots are assigned their rank.
    """

    _assigned_property: str  # property name for assigned origin time
    _dstream_algo: types.ModuleType  # downstream algorithm of surfaces
    _t0: typing.Union[int, str]  # origin time offset, or property name

    def __init__(
        self: "AssignOriginTimeGeometricTriePostprocessor",
        dstream_algo: typing.Union[str, types.ModuleType],
        assigned_property: str = "origin_time",
        *,
        t0: typing.Union[int, str] = "dstream_S",
    ) -> None:
        """Initialize functor instance.

        Parameters
        ----------
        dstream_algo : str or module
            Downstream algorithm used to curate surfaces, used to look up
            retained ranks.

            For example, `"dstream.steady_algo"` or `dstream.steady_algo`.
        assigned_property : str, default "origin_time"
            The property name for the assigned origin time.
        t0 : int or str, default "dstream_S"
            The property name or constant value for the origin time offset.

            Assigned origin times are relative to `t0`, and origin times
            before `t0` are considered impossible.
        """
        self._dstream_algo = _resolve_dstream_algo(dstream_algo)
        self._assigned_property = assigned_property
        self._t0 = t0

    def __call__(
        self: "AssignOriginTimeGeometricTriePostprocessor",
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

            Tries must have contiguous ids, be topologically sorted, and
            provide `rank` and `dstream_S` columns.
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
            if not mutate:
                trie = trie.clone()
            return _call_polars(self, trie, p_differentia_collision)
        else:
            raise TypeError  # pragma: no cover
