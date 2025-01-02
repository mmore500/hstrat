import logging
import typing

import polars as pl
from tqdm import tqdm

from .._auxiliary_lib import (
    alifestd_assign_contiguous_ids,
    alifestd_collapse_trunk_asexual,
    alifestd_collapse_unifurcations,
    get_sole_scalar_value_polars,
    log_context_duration,
    log_memory_usage,
    render_pandas_snapshot,
    render_polars_snapshot,
)
from ..phylogenetic_inference.tree.trie_postprocess import NopTriePostprocessor


def surface_postprocess_trie(
    df: pl.DataFrame,
    *,
    trie_postprocessor: typing.Callable = NopTriePostprocessor(),
    # ^^^ NopTriePostprocessor is stateless, so is safe as default value
) -> pl.DataFrame:
    """Postprocess raw phylogenetic tree reconstruction output data to create
    finalized estimate of phylogenetic history.

    Perfoms the following operations:
    - Collapse trunk nodes with rank less than `dstream_S`.
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
            - 'rank' : pl.UInt64
                - Num generations elapsed for ancestral differentia.
                - Corresponds to`dstream_Tbar` for inner nodes.
                - Corresponds `dstream_T` - 1 for leaf nodes
            - 'differentia_bitwidth' : pl.UInt32
                - Size of annotation differentiae, in bits.
                - Corresponds to `dstream_value_bitwidth`.
            - 'dstream_S' : pl.UInt32
                - Capacity of dstream buffer used for hstrat surface, in number
                  of data items (i.e., differentia values).

        Optional schema:
            - 'dstream_data_id' : pl.UInt64
                - Unique identifier for each genome in source genomedataframe

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
    original_columns = df.columns

    logging.info("extracting differentia bitwidth")
    differentia_bitwidth = get_sole_scalar_value_polars(
        df, "differentia_bitwidth"
    )
    logging.info(f" - differentia bitwidth: {differentia_bitwidth}")

    logging.info("converting DataFrame to Pandas...")
    with log_context_duration("pl.DataFrame.to_pandas", logging.info):
        df = df.to_pandas()
    render_pandas_snapshot(df, "as pandas", logging.info)
    log_memory_usage(logging.info)

    with log_context_duration("alifestd_collapse_trunk_asexual", logging.info):
        df["is_trunk"] = df["rank"] < df["dstream_S"]
        render_pandas_snapshot(df[5:], display=print)
        df = alifestd_collapse_trunk_asexual(df, mutate=True)

    with log_context_duration("alifestd_collapse_unifurcations", logging.info):
        df = alifestd_collapse_unifurcations(df, mutate=True)

    render_pandas_snapshot(df, "collapsed tree", logging.info)

    with log_context_duration("alifestd_assign_contiguous_ids", logging.info):
        df = alifestd_assign_contiguous_ids(df, mutate=True)

    render_pandas_snapshot(df, "reassigned tree", logging.info)

    with log_context_duration("trie_postprocessor", logging.info):
        df = trie_postprocessor(
            df,
            p_differentia_collision=2**-differentia_bitwidth,
            mutate=True,
            progress_wrap=tqdm,
        )
    render_pandas_snapshot(df, "with trie postprocessing", logging.info)

    to_keep = {*original_columns} - {"differentia_bitwidth", "dstream_S"}
    to_drop = {*df.columns} - to_keep
    logging.info(f"dropping columns {to_drop=}...")
    df.drop(columns=[*to_drop], inplace=True)

    logging.info("converting DataFrame to Polars...")
    with log_context_duration("pl.from_pandas", logging.info):
        df = pl.from_pandas(df)
    render_polars_snapshot(df, "as polars", logging.info)
    log_memory_usage(logging.info)

    return df
