"""Comparable-rank bounds shared by geometric origin-time postprocessors."""

import logging

from phyloframe import legacy as pfl
import polars as pl

from ....._auxiliary_lib import log_context_duration


def mark_inner_node_bounds(trie: pl.DataFrame) -> pl.DataFrame:
    """Mark inner nodes, i.e., nodes whose children diverged from one
    another, and the bounds of their comparable ranks.

    Returns `rank` (Int64) and added columns, per node:
    - `is_inner`: does node bound divergence among its children?
    - `compare_T`: `dstream_T` at which its children's differentiae are
      compared, i.e., the largest of their minimum tip `dstream_T`, as ranks
      retained there are retained by every child's youngest tip
    - `clade_min_T`: minimum tip `dstream_T` over its clade

    Trie must have contiguous ids, be topologically sorted, and provide an
    integer `rank` column, with leaf rank `dstream_T - 1`.
    """
    marked = trie.select(pl.col("id", "ancestor_id", "rank").cast(pl.Int64))
    with log_context_duration("mark_inner_node_bounds", logging.info):
        marked = pfl.alifestd_mark_num_children_polars(marked)
        marked = marked.with_columns(
            # leaf rank is dstream_T - 1
            _tip_T=pl.when(pl.col("num_children") == 0).then(
                pl.col("rank") + 1
            ),
        )
        marked = pfl.alifestd_mark_lineage_cummin_polars(
            marked, "_tip_T", reverse=True, mark_as="clade_min_T"
        )
        marked = pfl.alifestd_mark_max_child_value_polars(
            marked.with_columns(pl.col("clade_min_T").cast(pl.Int64)),
            "clade_min_T",
            mark_as="compare_T",
        )

    # roots with multiple children bound divergence like inner nodes
    return marked.select(
        "rank",
        is_inner=(pl.col("num_children") >= 2)
        | (
            (pl.col("num_children") == 1)
            & (pl.col("id") != pl.col("ancestor_id"))
        ),
        compare_T=pl.col("compare_T").cast(pl.Int64),
        clade_min_T=pl.col("clade_min_T"),
    )
