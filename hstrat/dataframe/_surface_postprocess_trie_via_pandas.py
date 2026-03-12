import gc
import logging
import typing

import pandas as pd
from phyloframe import legacy as pfl
import polars as pl
from tqdm import tqdm

from .._auxiliary_lib import (
    get_sole_scalar_value_polars,
    log_context_duration,
    log_memory_usage,
    render_pandas_snapshot,
    render_polars_snapshot,
)
from ..phylogenetic_inference.tree.trie_postprocess import NopTriePostprocessor


def _apply_empty_output_schema_pandas(
    df: pd.DataFrame,
    drop_dstream_metadata: typing.Optional[bool] = None,
) -> pd.DataFrame:
    """Transform an empty trie DataFrame to match the postprocessed output
    schema: add ``hstrat_rank`` and drop internal-only columns."""
    if "dstream_rank" in df.columns and "dstream_S" in df.columns:
        df["hstrat_rank"] = df["dstream_rank"] - df["dstream_S"]
    # phyloframe may have cast ancestor_id to int64; restore documented uint64
    if "ancestor_id" in df.columns:
        df["ancestor_id"] = df["ancestor_id"].astype("uint64")
    if drop_dstream_metadata is not False:
        logging.info("dropping dstream metadata from empty output")
        df = df.drop(
            columns=[
                "dstream_rank",
                "dstream_S",
                "hstrat_differentia_bitwidth",
            ],
            errors="ignore",
        )
    return df


def _do_collapse_unifurcations(
    df: pd.DataFrame,
) -> pd.DataFrame:
    with log_context_duration("alifestd_assign_contiguous_ids", logging.info):
        df = pfl.alifestd_assign_contiguous_ids(df, mutate=True)

    gc.collect()

    with log_context_duration("alifestd_collapse_unifurcations", logging.info):
        df = pfl.alifestd_collapse_unifurcations(df, mutate=True)

    render_pandas_snapshot(df, "collapsed tree", logging.info)

    gc.collect()

    return df


def _do_delete_trunk(
    df: pd.DataFrame,
) -> pd.DataFrame:
    with log_context_duration("alifestd_assign_contiguous_ids", logging.info):
        df = pfl.alifestd_assign_contiguous_ids(df, mutate=True)

    gc.collect()

    with log_context_duration(
        "df['dstream_S'].unique().squeeze()", logging.info
    ):
        dstream_S = df["dstream_S"].unique().squeeze()

    df["is_trunk"] = df["dstream_rank"] < df["dstream_S"] - 1
    df["origin_time"] = df["dstream_rank"]

    with log_context_duration("alifestd_delete_trunk_asexual", logging.info):
        df = pfl.alifestd_delete_trunk_asexual(df, mutate=True)

    if df.empty:
        logging.warning("empty dataframe after trunk deletion")
        df = df.drop(
            columns=["is_trunk", "ancestor_is_trunk", "origin_time"],
            errors="ignore",
        )
        return df

    with log_context_duration("alifestd_assign_contiguous_ids", logging.info):
        df = pfl.alifestd_assign_contiguous_ids(df, mutate=True)

    with log_context_duration("alifestd_prefix_roots", logging.info):
        # extend newly-clipped roots all the way back to dstream_S boundary
        df = pfl.alifestd_prefix_roots(
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
        df = pfl.alifestd_assign_contiguous_ids(df, mutate=True)

    gc.collect()

    render_pandas_snapshot(df, "reassigned tree", logging.info)

    return df


def _surface_postprocess_trie_via_pandas(
    df: pl.DataFrame,
    *,
    drop_dstream_metadata: typing.Optional[bool] = None,
    trie_postprocessor: typing.Callable = NopTriePostprocessor(),
    delete_trunk: bool = True,
    # ^^^ NopTriePostprocessor is stateless, so is safe as default value
) -> pl.DataFrame:
    """Legacy implementation of trie postprocessing using Pandas, kept for
    testing purposes. Should not be used in production code."""
    logging.info("beginning surface_postprocess_trie")
    log_memory_usage(logging.info)
    render_polars_snapshot(df, "raw tree", logging.info)

    if df.lazy().limit(1).collect().is_empty():
        logging.warning("empty input dataframe, returning empty result")
        from ._surface_postprocess_trie import _apply_empty_output_schema

        return _apply_empty_output_schema(df, drop_dstream_metadata)

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

    if df.empty:
        logging.warning("empty dataframe after trunk deletion, returning")
        return pl.from_pandas(
            _apply_empty_output_schema_pandas(df, drop_dstream_metadata),
        )

    df = _do_collapse_unifurcations(df)

    df = _do_assign_contiguous_ids(df)

    with log_context_duration("trie_postprocessor", logging.info):
        pre_postprocessor_columns = {*df.columns}
        # Cast to signed to prevent uint64 underflow when
        # dstream_rank < dstream_S (possible after trunk deletion
        # with the S-1 threshold for zero-gen surfaces).
        df["dstream_rank"] = df["dstream_rank"].astype("Int64")
        df["dstream_S"] = df["dstream_S"].astype("Int64")
        df = df.rename(columns={"dstream_rank": "rank"})
        df = trie_postprocessor(
            df,
            p_differentia_collision=2**-differentia_bitwidth,
            mutate=True,
            progress_wrap=tqdm,
        )
        df = df.rename(columns={"rank": "dstream_rank"})

    render_pandas_snapshot(df, "with trie postprocessing", logging.info)

    logging.info("setting up hstrat_rank...")
    df["hstrat_rank"] = df["dstream_rank"].astype("Int64") - df[
        "dstream_S"
    ].astype("Int64")

    to_keep = {*original_columns}
    if drop_dstream_metadata is not False:
        to_keep -= {"dstream_rank", "dstream_S", "hstrat_differentia_bitwidth"}
    to_drop = pre_postprocessor_columns - to_keep
    logging.info(f"dropping columns {to_drop=}...")
    df.drop(columns=[*to_drop], inplace=True)
    gc.collect()

    logging.info("converting DataFrame to Polars...")
    with log_context_duration("pl.from_pandas", logging.info):
        df = pl.from_pandas(df)

    # phyloframe may change id/ancestor_id types; restore documented UInt64
    df = df.cast({"id": pl.UInt64, "ancestor_id": pl.UInt64})

    gc.collect()
    render_polars_snapshot(df, "as polars", logging.info)
    log_memory_usage(logging.info)

    return df
