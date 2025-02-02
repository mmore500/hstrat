import gc
import logging
import typing

import pandas as pd
import polars as pl
from tqdm import tqdm

from .._auxiliary_lib import (
    alifestd_assign_contiguous_ids,
    alifestd_collapse_unifurcations,
    alifestd_delete_trunk_asexual,
    alifestd_prefix_roots,
    get_sole_scalar_value_polars,
    log_context_duration,
    log_memory_usage,
    render_pandas_snapshot,
    render_polars_snapshot,
)
from ..phylogenetic_inference.tree.trie_postprocess import NopTriePostprocessor


def _do_collapse_unifurcations(
    df: pd.DataFrame,
) -> pd.DataFrame:
    with log_context_duration("alifestd_assign_contiguous_ids", logging.info):
        df = alifestd_assign_contiguous_ids(df, mutate=True)

    gc.collect()

    with log_context_duration("alifestd_collapse_unifurcations", logging.info):
        df = alifestd_collapse_unifurcations(df, mutate=True)

    render_pandas_snapshot(df, "collapsed tree", logging.info)

    gc.collect()

    return df


def _do_delete_trunk(
    df: pd.DataFrame,
) -> pd.DataFrame:
    with log_context_duration("alifestd_assign_contiguous_ids", logging.info):
        df = alifestd_assign_contiguous_ids(df, mutate=True)

    gc.collect()

    with log_context_duration(
        "df['dstream_S'].unique().squeeze()", logging.info
    ):
        dstream_S = df["dstream_S"].unique().squeeze()

    df["is_trunk"] = df["hstrat_rank"] < df["dstream_S"]
    df["origin_time"] = df["hstrat_rank"]

    with log_context_duration("alifestd_delete_trunk_asexual", logging.info):
        df = alifestd_delete_trunk_asexual(df, mutate=True)

    with log_context_duration("alifestd_assign_contiguous_ids", logging.info):
        df = alifestd_assign_contiguous_ids(df, mutate=True)

    with log_context_duration("alifestd_prefix_roots", logging.info):
        # extend newly-clipped roots all the way back to dstream_S boundary
        df = alifestd_prefix_roots(
            df, allow_id_reassign=True, origin_time=dstream_S, mutate=True
        )

    del df["is_trunk"]
    del df["ancestor_is_trunk"]
    del df["origin_time"]
    gc.collect()

    return df


def _do_assign_contiguous_ids(
    df: pd.DataFrame,
) -> pd.DataFrame:
    with log_context_duration("alifestd_assign_contiguous_ids", logging.info):
        df = alifestd_assign_contiguous_ids(df, mutate=True)

    gc.collect()

    render_pandas_snapshot(df, "reassigned tree", logging.info)

    return df


def surface_postprocess_trie(
    df: pl.DataFrame,
    *,
    trie_postprocessor: typing.Callable = NopTriePostprocessor(),
    delete_trunk: bool = True,
    # ^^^ NopTriePostprocessor is stateless, so is safe as default value
) -> pl.DataFrame:
    """Postprocess raw phylogenetic tree reconstruction output data to create
    finalized estimate of phylogenetic history.

    Perfoms the following operations:
    - Delete trunk nodes with rank less than `dstream_S`.
    - Collapse unifurcations.
    - Assign contiguous IDs to nodes.
    - Apply supplied `trie_postprocessor` functor.

    Parameters
    ----------
    df : pl.DataFrame
        The input DataFrame containing packed data with required columns, one
        row per genome.

        Required schema:
            - 'id' : pl.UInt64
                - Unique identifier for each taxon (RE alife standard format).
            - 'ancestor_id' : pl.UInt64
                - Unique identifier for ancestor taxon  (RE alife standard
                  format).
            - 'hstrat_rank' : pl.UInt64
                - Num generations elapsed for ancestral differentia.
                - Corresponds to `dstream_Tbar` for inner nodes.
                - Corresponds `dstream_T` - 1 for leaf nodes
            - 'hstrat_differentia_bitwidth' : pl.UInt32
                - Size of annotation differentiae, in bits.
                - Corresponds to `dstream_value_bitwidth`.
            - 'dstream_S' : pl.UInt32
                - Capacity of dstream buffer used for hstrat surface, in number
                  of data items (i.e., differentia values).

        Optional schema:
            - 'dstream_data_id' : pl.UInt64
                - Unique identifier for each genome in source genomedataframe

    delete_trunk : bool, default `True`
        Should trunk nodes with rank less than `dstream_S` be deleted?

        Trunk deletion accounts for "dummy" strata added to fill hstrat surface
        for founding ancestor(s), by segregating subtrees with distinct
        founding strata into independent trees.

    trie_postprocessor : Callable, default `hstrat.NopTriePostprocessor()`
        Tree postprocess functor.

        Must take `trie` of type `pandas.DataFrame`,
        `p_differentia_collision` of type `float`, `mutate` of type `bool`, and
        `progress_wrap` of type `Callable` params. Must returned postprocessed
        trie (type `pd.DataFrame`).

        To apply multiple postprocessors, use
        `hstrat.CompoundTriePostprocessor`.

    Returns
    -------
    pl.DataFrame
        The output DataFrame containing the estimated phylogenetic tree in
        alife standard format, with the following columns:

        Required schema:
        - 'id' : pl.UInt64
            - Unique identifier for each taxon (RE alife standard format).
        - 'ancestor_id' : pl.UInt64
            - Unique identifier for ancestor taxon  (RE alife standard format).
        - 'hstrat_rank_from_t0' : pl.UInt64
            - Num generations elapsed for ancestral differentia.
            - Corresponds to `dstream_Tbar` - `dstream_S` for inner nodes.
            - Corresponds `dstream_T` - 1 - `dstream_S` for leaf nodes

        Optional schema:
        - 'origin_tme' : pl.UInt64
            - Estimated origin time for phylogeny nodes, in generations elapsed
              since fouding ancestor.

              Value depends on the trie postprocessor used.

        Additional user-defined columns will be forwarded from the input
        DataFrame. Any columns created by the trie postprocessor will also be
        included.

        Note that the alife-standard `ancestor_list` column is not included in
        the output.

    Notes
    -----
    Collapsing trunk nodes with rank less than `dstream_S` assumes that `S`
    "dummy" strata were added to fill hstrat surface for founding ancestor(s).

    Currently, data is converted to Pandas for processing, then back to Polars.

    See Also
    --------
    surface_unpack_reconstruct :
        Creates raw reconstruction data postprocessed here.
    alifestd_try_add_ancestor_list_col :
        Adds alife-standard `ancestor_list` column to phylogeny data.
    """
    logging.info("beginning surface_postprocess_trie")
    log_memory_usage(logging.info)
    render_polars_snapshot(df, "raw tree", logging.info)

    logging.info("extracting differentia bitwidth")
    differentia_bitwidth = get_sole_scalar_value_polars(
        df, "hstrat_differentia_bitwidth"
    )
    logging.info(f" - differentia bitwidth: {differentia_bitwidth}")

    logging.info("converting DataFrame to Pandas...")
    with log_context_duration("pl.DataFrame.to_pandas", logging.info):
        df = df.lazy().collect().to_pandas()
    render_pandas_snapshot(df, "as pandas", logging.info)
    log_memory_usage(logging.info)
    original_columns = df.columns

    if delete_trunk:
        df = _do_delete_trunk(df)

    df = _do_collapse_unifurcations(df)

    df = _do_assign_contiguous_ids(df)

    with log_context_duration("trie_postprocessor", logging.info):
        pre_postprocessor_columns = {*df.columns}
        df = df.rename(columns={"hstrat_rank": "rank"})
        df = trie_postprocessor(
            df,
            p_differentia_collision=2**-differentia_bitwidth,
            mutate=True,
            progress_wrap=tqdm,
        )
        df = df.rename(columns={"rank": "hstrat_rank"})

    render_pandas_snapshot(df, "with trie postprocessing", logging.info)

    logging.info("setting up hstrat_rank_from_t0...")
    df["hstrat_rank_from_t0"] = df["hstrat_rank"] - df["dstream_S"]

    to_keep = {*original_columns} - {
        "dstream_S",
        "hstrat_differentia_bitwidth",
        "hstrat_rank",
    }
    to_drop = pre_postprocessor_columns - to_keep
    logging.info(f"dropping columns {to_drop=}...")
    df.drop(columns=[*to_drop], inplace=True)
    gc.collect()

    logging.info("converting DataFrame to Polars...")
    with log_context_duration("pl.from_pandas", logging.info):
        df = pl.from_pandas(df)
    gc.collect()
    render_polars_snapshot(df, "as polars", logging.info)
    log_memory_usage(logging.info)

    return df
