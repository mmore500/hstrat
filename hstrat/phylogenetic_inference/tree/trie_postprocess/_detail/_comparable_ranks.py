"""Comparable-rank lookups shared by geometric origin-time postprocessors."""

import logging
import types
import typing

import numpy as np
from phyloframe import legacy as pfl
import polars as pl

from ....._auxiliary_lib import (
    get_sole_scalar_value_polars,
    log_context_duration,
)


def get_sole_dstream_S(trie: pl.DataFrame) -> int:
    """Check trie preconditions and get its uniform `dstream_S`."""
    if not pfl.alifestd_has_contiguous_ids_polars(trie):
        raise NotImplementedError("non-contiguous ids not supported")
    if not pfl.alifestd_is_topologically_sorted_polars(trie):
        raise NotImplementedError("non-topologically-sorted not supported")
    if trie.is_empty():
        return 0
    return int(get_sole_scalar_value_polars(trie, "dstream_S"))


def _mark_comparison_bounds(
    trie: pl.DataFrame,
) -> typing.Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Mark, per node, its number of children, the `dstream_T` at which its
    children's differentiae are compared, and the minimum `dstream_T` over
    its clade.

    Children are compared at the largest of their minimum tip `dstream_T`,
    as ranks retained there are retained by every child's youngest tip.
    """
    # leaf rank is dstream_T - 1
    num_children = pfl.alifestd_mark_to_array_polars(
        trie, pfl.alifestd_mark_num_children_polars
    )
    trie = trie.with_columns(
        pl.when(pl.Series(num_children) == 0)
        .then(pl.col("rank") + 1)
        .otherwise(None)
        .alias("_tip_T"),
    )
    clade_min_T = pfl.alifestd_mark_to_array_polars(
        trie,
        pfl.alifestd_mark_lineage_cummin_polars,
        values="_tip_T",
        reverse=True,
    ).astype(np.int64)
    compare_T = pfl.alifestd_mark_to_array_polars(
        trie,
        pfl.alifestd_mark_max_child_value_polars,
        values=pl.Series(clade_min_T),
    ).astype(np.int64)
    return num_children, compare_T, clade_min_T


class InnerNodeBounds(typing.NamedTuple):
    """Comparison bounds for inner nodes, i.e., nodes whose children
    diverged from one another."""

    ranks: np.ndarray  # all nodes' ranks
    is_inner: np.ndarray  # is node inner?
    compare_T: np.ndarray  # dstream_T children are compared at, per inner
    clade_min_T: np.ndarray  # youngest tip dstream_T in clade, per inner


def mark_inner_node_bounds(trie: pl.DataFrame) -> InnerNodeBounds:
    """Mark inner nodes, and the bounds of their comparable ranks.

    Trie must have contiguous ids, be topologically sorted, and provide an
    integer `rank` column, with leaf rank `dstream_T - 1`.
    """
    ranks = trie["rank"].cast(pl.Int64).to_numpy()
    with log_context_duration("_mark_comparison_bounds", logging.info):
        num_children, compare_T, clade_min_T = _mark_comparison_bounds(
            trie.select(pl.col("id", "ancestor_id", "rank").cast(pl.Int64)),
        )
    # roots with multiple children bound divergence like inner nodes
    is_inner = num_children >= 2
    is_inner |= (num_children == 1) & (
        trie["id"].to_numpy() != trie["ancestor_id"].to_numpy()
    )
    return InnerNodeBounds(
        ranks, is_inner, compare_T[is_inner], clade_min_T[is_inner]
    )


def iter_retained_ranks(
    dstream_algo: types.ModuleType,
    dstream_S: int,
    T: np.ndarray,
    chunk_size: int = 2**16,
) -> typing.Iterator[typing.Tuple[slice, np.ndarray]]:
    """Yield chunks of rows, and the ranks retained at each row's `T`,
    sorted ascending, as floats."""
    for begin in range(0, len(T), chunk_size):
        chunk = slice(begin, begin + chunk_size)
        unique_T, inverse = np.unique(T[chunk], return_inverse=True)
        retained = dstream_algo.lookup_ingest_times_batched(
            dstream_S, unique_T.astype(np.uint64), parallel=True
        ).astype(np.float64)[inverse]
        yield chunk, np.sort(retained, axis=1)


def first_retained_between(
    retained: np.ndarray,
    after: np.ndarray,
    before: np.ndarray,
    num: int,
) -> np.ndarray:
    """First `num` sorted `retained` ranks strictly between `after` and
    `before`, per row (inf if none)."""
    # index of first rank after `after`, as rows are sorted ascending
    columns = (retained <= after[:, None]).sum(axis=1)[:, None] + np.arange(
        num
    )
    in_bounds = columns < retained.shape[1]
    result = np.take_along_axis(
        retained, np.minimum(columns, retained.shape[1] - 1), axis=1
    )
    return np.where(in_bounds & (result < before[:, None]), result, np.inf)
