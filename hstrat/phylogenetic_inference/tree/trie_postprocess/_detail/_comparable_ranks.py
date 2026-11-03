"""Comparable-rank bounds shared by surface origin-time postprocessors."""

import logging
import types

from phyloframe import legacy as pfl
import polars as pl

from ....._auxiliary_lib import (
    get_sole_scalar_value_polars,
    log_context_duration,
    resolve_dstream_algo,
)


def mark_inner_node_bounds(trie_df: pl.DataFrame) -> pl.DataFrame:
    """Mark leaves and roots, and the bounds of nodes' comparable ranks.

    Inner nodes, i.e., nodes that are neither leaves nor roots, are those
    `~is_leaf & ~is_root`.

    Returns `rank` (Int64) and added columns, per node:
    - `is_leaf`: is node a leaf?
    - `is_root`: is node a root?
    - `num_mrca_leaf_pairs`: number of leaf pairs whose most recent common
      ancestor is node
    - `compare_T`: `dstream_T` at which its children's differentiae are
      compared, i.e., the largest of their minimum tip `dstream_T`, as ranks
      retained there are retained by every child's youngest tip
    - `clade_min_T`: minimum tip `dstream_T` over its clade

    Trie must have contiguous ids, be topologically sorted, and provide an
    integer `rank` column, with leaf rank `dstream_T - 1`.
    """
    marked_df = trie_df.lazy().select(
        pl.col("id", "ancestor_id", "rank").cast(pl.Int64),
    )
    with log_context_duration("mark_inner_node_bounds", logging.info):
        marked_df = pfl.alifestd_mark_leaves_polars(marked_df)
        marked_df = pfl.alifestd_mark_roots_polars(marked_df)
        marked_df = marked_df.with_columns(
            # leaf rank is dstream_T - 1
            _tip_T=pl.when("is_leaf").then(pl.col("rank") + 1),
        )
        marked_df = pfl.alifestd_mark_lineage_cummin_polars(
            marked_df, "_tip_T", reverse=True, mark_as="clade_min_T"
        )
        marked_df = pfl.alifestd_mark_max_child_value_polars(
            marked_df.with_columns(pl.col("clade_min_T").cast(pl.Int64)),
            "clade_min_T",
            mark_as="compare_T",
        )
        marked_df = pfl.alifestd_mark_num_mrca_leaf_pairs_polars(marked_df)

        bounds_df = marked_df.select(
            "rank",
            "is_leaf",
            "is_root",
            "num_mrca_leaf_pairs",
            compare_T=pl.col("compare_T"),
            clade_min_T=pl.col("clade_min_T"),
        ).collect()

    # children are compared no earlier than the clade's youngest tip
    assert (bounds_df["compare_T"] >= bounds_df["clade_min_T"]).all()
    return bounds_df


def get_dstream_algo(trie_df: pl.DataFrame) -> types.ModuleType:
    """Look up the trie's uniform `dstream_algo` column, as attached by
    `surface_unpack_reconstruct`."""
    if "dstream_algo" not in trie_df.columns:
        raise ValueError(
            "trie has no dstream_algo column, as attached by "
            "surface_unpack_reconstruct",
        )
    return resolve_dstream_algo(
        str(get_sole_scalar_value_polars(trie_df, "dstream_algo")),
    )
