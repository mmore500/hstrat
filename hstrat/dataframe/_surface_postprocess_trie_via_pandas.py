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


def _surface_postprocess_trie_via_pandas(
    df: pl.DataFrame,
    *,
    trie_postprocessor: typing.Callable = NopTriePostprocessor(),
    delete_trunk: bool = True,
    # ^^^ NopTriePostprocessor is stateless, so is safe as default value
) -> pl.DataFrame:
    """Legacy implementation of trie postprocessing using Pandas, kept for
    testing purposes. Should not be used in production code."""
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
