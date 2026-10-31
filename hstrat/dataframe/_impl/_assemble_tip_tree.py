import logging
import typing

import numpy as np
import polars as pl
from tqdm import tqdm

from ..._auxiliary_lib import log_context_duration, render_polars_snapshot
from ._surface_explode_tips import SurfaceTips
from ._surface_unpack_reconstruct import _join_user_defined_columns


def assemble_tip_tree(
    df: pl.DataFrame,
    tips: SurfaceTips,
    parent: np.ndarray,
    time: np.ndarray,
    *,
    drop_dstream_metadata: typing.Optional[bool],
    trie_postprocessor: typing.Callable,
) -> pl.DataFrame:
    """Convert a tree over tips into an alife standard phylogeny dataframe.

    Parameters
    ----------
    df : pl.DataFrame
        Packed genome data the tips came from, for user-defined columns.
    tips : SurfaceTips
        Tip data, in the order of the tree's first `len(tips)` nodes.
    parent : np.ndarray
        Parent of each node, with tips first and each parent after its
        children; roots are their own parent.
    time : np.ndarray
        Origin time of each inner node (tip entries are ignored).
    drop_dstream_metadata : bool or None
        As for `surface_unpack_reconstruct`.
    trie_postprocessor : Callable
        Functor applied to the assembled phylogeny before it is returned,
        with the same call signature as for `surface_postprocess_trie`.

    Returns
    -------
    pl.DataFrame
        Phylogeny with contiguous, topologically sorted ids (ancestors
        first), and columns `id`, `ancestor_id`, `origin_time`, and
        `dstream_data_id` (null for inner nodes), plus user-defined columns
        joined onto leaves.
    """
    n_tips, n_nodes = len(tips), len(parent)
    time = np.asarray(time, dtype=np.float64).copy()
    time[:n_tips] = tips.leaf_origin_times()

    # reverse node order, so that ancestors precede descendants
    reverse = n_nodes - 1 - np.arange(n_nodes, dtype=np.int64)
    data_id = np.zeros(n_nodes, dtype=np.uint64)
    data_id[:n_tips] = tips.data_id
    is_tip = np.arange(n_nodes) < n_tips
    phylo_df = pl.DataFrame(
        {
            "id": reverse[::-1],
            "ancestor_id": reverse[np.asarray(parent, dtype=np.int64)][::-1],
            "dstream_data_id": pl.Series(
                np.where(is_tip, data_id, 0)[::-1], dtype=pl.UInt64
            ),
            "_is_tip": is_tip[::-1],
        },
        schema={
            "id": pl.UInt64,
            "ancestor_id": pl.UInt64,
            "dstream_data_id": pl.UInt64,
            "_is_tip": pl.Boolean,
        },
    ).with_columns(
        dstream_data_id=pl.when(pl.col("_is_tip")).then(
            pl.col("dstream_data_id"),
        ),
    )
    phylo_df = phylo_df.drop("_is_tip")
    render_polars_snapshot(phylo_df, "assembled tree", logging.info)

    with log_context_duration("_join_user_defined_columns", logging.info):
        phylo_df = _join_user_defined_columns(
            df, phylo_df, drop_dstream_metadata
        )

    # assign after joining, overwriting any user-defined origin_time
    phylo_df = phylo_df.with_columns(
        pl.Series("origin_time", time[::-1], dtype=pl.Float64),
    )

    with log_context_duration("trie_postprocessor", logging.info):
        phylo_df = trie_postprocessor(
            phylo_df,
            p_differentia_collision=tips.p_differentia_collision,
            mutate=True,
            progress_wrap=tqdm,
        )

    render_polars_snapshot(phylo_df, "postprocessed tree", logging.info)
    return phylo_df
