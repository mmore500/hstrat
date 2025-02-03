import functools
import gc
import logging
import os
import typing
import warnings

from pandas import testing as pdt
import polars as pl
from tqdm import tqdm

from .._auxiliary_lib import (
    alifestd_assign_contiguous_ids_polars,
    alifestd_collapse_unifurcations_polars,
    alifestd_delete_trunk_asexual_polars,
    alifestd_prefix_roots_polars,
    get_sole_scalar_value_polars,
    is_in_unit_test,
    log_context_duration,
    log_memory_usage,
    render_polars_snapshot,
)
from ..phylogenetic_inference.tree.trie_postprocess import NopTriePostprocessor
from ._surface_postprocess_trie_via_pandas import (
    _surface_postprocess_trie_via_pandas,
)


def _do_collapse_unifurcations(
    df: pl.DataFrame,
) -> pl.DataFrame:
    with log_context_duration("alifestd_assign_contiguous_ids", logging.info):
        df = alifestd_assign_contiguous_ids_polars(df)

    gc.collect()

    with log_context_duration("alifestd_collapse_unifurcations", logging.info):
        df = alifestd_collapse_unifurcations_polars(df)

    render_polars_snapshot(df, "collapsed tree", logging.info)

    gc.collect()

    return df


def _do_delete_trunk(
    df: pl.DataFrame,
) -> pl.DataFrame:
    with log_context_duration("alifestd_assign_contiguous_ids", logging.info):
        df = alifestd_assign_contiguous_ids_polars(df)

    gc.collect()

    with log_context_duration("get_sole_scalar_value_polars", logging.info):
        dstream_S = get_sole_scalar_value_polars(df, "dstream_S")

    df = df.with_columns(
        is_trunk=pl.col("hstrat_rank") < dstream_S,
        origin_time=pl.col("hstrat_rank"),
    )

    with log_context_duration("alifestd_delete_trunk_asexual", logging.info):
        df = alifestd_delete_trunk_asexual_polars(df)

    with log_context_duration("alifestd_assign_contiguous_ids", logging.info):
        df = alifestd_assign_contiguous_ids_polars(df)

    with log_context_duration("alifestd_prefix_roots", logging.info):
        # extend newly-clipped roots all the way back to dstream_S boundary
        df = alifestd_prefix_roots_polars(
            df, allow_id_reassign=True, origin_time=dstream_S
        )

    gc.collect()

    return df.drop(
        ["is_trunk", "ancestor_is_trunk", "origin_time"], strict=False
    )


def _do_assign_contiguous_ids(
    df: pl.DataFrame,
) -> pl.DataFrame:
    with log_context_duration("alifestd_assign_contiguous_ids", logging.info):
        df = alifestd_assign_contiguous_ids_polars(df)

    gc.collect()

    render_polars_snapshot(df, "reassigned tree", logging.info)

    return df


def _validate_against_via_pandas(func: typing.Callable) -> typing.Callable:
    """Decorator to validate Polars impl against equivalent Pandas impl."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> pl.DataFrame:
        result = func(*args, **kwargs)
        if "CI" in os.environ or is_in_unit_test():
            warnings.warn(
                "CI environment detected, performing extra validation tests",
            )
            expected = _surface_postprocess_trie_via_pandas(*args, **kwargs)
            # convert to pandas to avoid Polars StringCache issues
            pdt.assert_frame_equal(
                result.to_pandas(),
                expected.to_pandas(),
                check_dtype=False,
                check_like=True,
            )
        return result

    return wrapper


@_validate_against_via_pandas
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
        trie (type `pl.DataFrame`).

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

    original_columns = df.columns

    if delete_trunk:
        df = _do_delete_trunk(df)

    df = _do_collapse_unifurcations(df)

    df = _do_assign_contiguous_ids(df)

    with log_context_duration("trie_postprocessor", logging.info):
        pre_postprocessor_columns = {*df.columns}
        df = df.rename({"hstrat_rank": "rank"})
        df = trie_postprocessor(
            df,
            p_differentia_collision=2**-differentia_bitwidth,
            mutate=True,
            progress_wrap=tqdm,
        )
        df = df.rename({"rank": "hstrat_rank"})

    render_polars_snapshot(df, "with trie postprocessing", logging.info)

    logging.info("setting up hstrat_rank_from_t0...")
    df = df.with_columns(
        hstrat_rank_from_t0=pl.col("hstrat_rank") - pl.col("dstream_S"),
    )

    to_keep = {*original_columns} - {
        "dstream_S",
        "hstrat_differentia_bitwidth",
        "hstrat_rank",
    }
    to_drop = pre_postprocessor_columns - to_keep
    logging.info(f"dropping columns {to_drop=}...")
    df = df.drop(*to_drop)

    render_polars_snapshot(df, "as polars", logging.info)
    gc.collect()
    log_memory_usage(logging.info)

    return df
