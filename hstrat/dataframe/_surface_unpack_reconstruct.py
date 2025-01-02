import logging
import math

from downstream import dataframe as dstream_dataframe
import pandas as pd
import polars as pl
import tqdm

from .._auxiliary_lib import (
    alifestd_make_empty,
    get_sole_scalar_value_polars,
    log_context_duration,
    log_memory_usage,
    render_polars_snapshot,
)
from ..phylogenetic_inference.tree._impl._build_tree_searchtable_cpp_impl_stub import (
    Records,
    collapse_dropped_unifurcations,
    extend_tree_searchtable_cpp_from_exploded,
    records_to_dict,
)


def _build_records_chunked(
    df: pl.DataFrame, exploded_slice_size: int
) -> Records:
    """Build tree searchtable from DataFrame, exploding in chunks to reduce
    memory usage."""
    num_slices = math.ceil(len(df) / exploded_slice_size)
    logging.info(f"{len(df)=} {exploded_slice_size=} {num_slices=}")

    init_size = len(df) * 8
    records = Records(init_size)
    for i, df_slice in enumerate(df.iter_slices(exploded_slice_size)):
        logging.info(f"incorporating slice {i + 1}/{num_slices}...")

        with log_context_duration(
            f"dstream.dataframe.explode_lookup_unpacked ({i + 1}/{num_slices})",
            logging.info,
        ):
            long_df = dstream_dataframe.explode_lookup_unpacked(
                df_slice, value_type="uint64"
            )

        with log_context_duration(
            '.sort_by("dstream_Tbar").over(partition_by="dstream_data_id") '
            f"({i + 1}/{num_slices})",
            logging.info,
        ):
            long_df = long_df.select(
                pl.col(
                    "dstream_data_id",
                    "dstream_T",
                    "dstream_Tbar",
                    "dstream_value",
                )
                .sort_by("dstream_Tbar")
                .over(partition_by="dstream_data_id"),
            )

        if i == 0:
            render_polars_snapshot(long_df, "exploded", logging.info)

        with log_context_duration(
            f"extend_tree_searchtable_cpp_from_exploded ({i + 1}/{num_slices})",
            logging.info,
        ):
            extend_tree_searchtable_cpp_from_exploded(
                records,
                long_df["dstream_data_id"].to_numpy(),
                long_df["dstream_T"].to_numpy(),
                long_df["dstream_Tbar"].to_numpy(),
                long_df["dstream_value"].to_numpy(),
                tqdm.tqdm,
            )

        with log_context_duration(
            f"collapse_dropped_unifurcations ({i + 1}/{num_slices})",
            logging.info,
        ):
            records = collapse_dropped_unifurcations(records)

        log_memory_usage(logging.info)

    return records


def _join_user_defined_columns(
    df: pl.DataFrame, phylo_df: pl.DataFrame
) -> pl.DataFrame:
    """Join user-defined columns from input data onto reconstructed tree
    dataframe."""
    df = df.select(
        pl.exclude("^dstream_.*$", "^downstream_.*$"),
        pl.col("dstream_data_id").cast(pl.UInt64),
    )
    joined_columns = set(df.columns) - set(phylo_df.columns)
    if joined_columns:
        logging.info(f" - {len(joined_columns)} column to join")
        logging.info(f" - joining columns: {[*joined_columns]}")
        phylo_df = phylo_df.join(df, on="dstream_data_id", how="left")
    else:
        logging.info(" - no columns to join, skipping")

    return phylo_df


def _construct_result_dataframe(
    records: Records,
    differentia_bitwidth: int,
    dstream_S: int,
) -> pl.DataFrame:
    """Convert tree searchtable records to DataFrame."""
    logging.info("converting records to dict...")
    records_dict = records_to_dict(records)

    logging.info("converting dict to dataframe...")
    del records_dict["differentia"]
    return (
        pl.from_dict(
            records_dict,  # type: ignore
            schema={
                "dstream_data_id": pl.UInt64,
                "id": pl.UInt64,
                "ancestor_id": pl.UInt64,
                "rank": pl.UInt64,
            },
        )
        .with_columns(
            pl.lit(differentia_bitwidth)
            .alias("hstrat_differentia_bitwidth")
            .cast(pl.UInt32),
            pl.lit(dstream_S).alias("dstream_S").cast(pl.UInt32),
        )
        .rename({"rank": "hstrat_rank"})
    )


def _surface_unpacked_reconstruct(
    df: pl.DataFrame,
    *,
    differentia_bitwidth: int,
    dstream_S: int,
    exploded_slice_size: int,
) -> pl.DataFrame:
    """Reconstruct phylogenetic tree from unpacked dstream data."""
    render_polars_snapshot(df, "unpacked", logging.info)

    logging.info("building tree searchtable chunkwise...")
    records = _build_records_chunked(df, exploded_slice_size)

    with log_context_duration("_construct_result_dataframe", logging.info):
        phylo_df = _construct_result_dataframe(
            records,
            differentia_bitwidth=differentia_bitwidth,
            dstream_S=dstream_S,
        )

    del records
    render_polars_snapshot(phylo_df, "converted", logging.info)

    logging.info("joining user-defined columns...")
    with log_context_duration("_join_user_defined_columns", logging.info):
        phylo_df = _join_user_defined_columns(df, phylo_df)

    logging.info("surface_unpack_reconstruct complete")
    render_polars_snapshot(phylo_df, "reconstruction", logging.info)

    return phylo_df


def surface_unpack_reconstruct(
    df: pl.DataFrame,
    *,
    exploded_slice_size: int = 1_000_000,
) -> pl.DataFrame:
    """Unpack dstream buffer and counter from genome data and construct an
    estimated phylogenetic tree for the genomes.

    Parameters
    ----------
    df : pl.DataFrame
        The input DataFrame containing packed data with required columns, one
        row per genome.

        Required schema:
            - 'data_hex' : pl.String
                - Raw genome data, with serialized dstream buffer and counter.
                - Represented as a hexadecimal string.
            - 'dstream_algo' : pl.Categorical
                - Name of downstream curation algorithm used.
                - e.g., 'dstream.steady_algo'
            - 'dstream_storage_bitoffset' : pl.UInt64
                - Position of dstream buffer field in 'data_hex'.
            - 'dstream_storage_bitwidth' : pl.UInt64
                - Size of dstream buffer field in 'data_hex'.
            - 'dstream_T_bitoffset' : pl.UInt64
                - Position of dstream counter field in 'data_hex'.
            - 'dstream_T_bitwidth' : pl.UInt64
                - Size of dstream counter field in 'data_hex'.
            - 'dstream_S' : pl.Uint32
                - Capacity of dstream buffer, in number of data items.

        Optional schema:
            - 'downstream_version' : pl.Categorical
                - Version of downstream library used to curate data items.
            - 'dstream_data_id' : pl.UInt64
                - Unique identifier for each data item.
                - If not provided, row number will be used as identifier.
            - 'downstream_exclude_exploded' : pl.Boolean
                - Should row be dropped after exploding unpacked data?
            - 'downstream_exclude_unpacked' : pl.Boolean
                - Should row be dropped after unpacking packed data?
            - 'downstream_validate_exploded' : pl.String, polars expression
                - Polars expression to validate exploded data.
            - 'downstream_validate_unpacked' : pl.String, polars expression
                - Polars expression to validate unpacked data.

    exploded_slice_size : int, default 1_000_000
        Number of rows to process at once. Lower values reduce memory usage.

    Returns
    -------
    pl.DataFrame
        The output DataFrame containing the estimated phylogenetic tree in
        alife standard format, with the following columns:

        - 'id' : pl.UInt64
            - Unique identifier for each taxon (RE alife standard format).
        - 'ancestor_id' : pl.UInt64
            - Unique identifier for ancestor taxon  (RE alife standard format).
        - 'hstrat_rank' : pl.UInt64
            - Num generations elapsed for ancestral differentia.
            - Corresponds to`dstream_Tbar` for inner nodes.
            - Corresponds `dstream_T` - 1 for leaf nodes
        - 'hstrat_differentia_bitwidth' : pl.UInt64
            - Size of annotation differentiae, in bits.
            - Corresponds to `dstream_value_bitwidth`.
        - 'dstream_S' : pl.UInt32
            - Capacity of dstream buffer, in number of data items.
        - 'dstream_data_id' : pl.UInt64
            - Unique identifier for each genome in source dataframe
            - Set to source dataframe row index if not provided.

        User-defined columns, except some prefixed with 'downstream_' or
        'dstream_', will be forwarded from the input DataFrame.

        Note that the alife-standard `ancestor_list` column is not included in
        the output.

    See Also
    --------
    surface_postprocess_trie :
        Post-processes raw phylogeny data, including collapsing superfluous
        internal nodes and estimating taxon origin times.
    alifestd_try_add_ancestor_list_col :
        Adds alife-standard `ancestor_list` column to phylogeny data.
    """
    logging.info("beginning surface_unpack_reconstruct")
    log_memory_usage(logging.info)

    render_polars_snapshot(df, "packed", logging.info)

    # for simplicity, return early for this special case
    if df.lazy().limit(1).collect().is_empty():
        logging.info("empty input dataframe, returning empty result")
        res = alifestd_make_empty()
        res["taxon_label"] = None
        res["hstrat_rank"] = pd.Series(dtype=int)
        res["hstrat_differentia_bitwidth"] = pd.Series(dtype=int)
        res["dstream_S"] = pd.Series(dtype=int)
        return pl.from_pandas(res)

    logging.info("extracting metadata...")
    dstream_storage_bitwidth = get_sole_scalar_value_polars(
        df, "dstream_storage_bitwidth"
    )
    logging.info(f" - dstream storage bitwidth: {dstream_storage_bitwidth}")

    dstream_S = get_sole_scalar_value_polars(df, "dstream_S")
    logging.info(f" - dstream S: {dstream_S}")

    if not dstream_storage_bitwidth % dstream_S == 0:
        raise ValueError(
            "dstream_storage_bitwidth must be a multiple of dstream_S, "
            "cannot calculate differentia_bitwidth",
        )
    differentia_bitwidth = dstream_storage_bitwidth // dstream_S
    logging.info(f" - differentia bitwidth: {differentia_bitwidth}")

    with log_context_duration(
        "dstream.dataframe.unpack_data_packed", logging.info
    ):
        df = dstream_dataframe.unpack_data_packed(df)

    return _surface_unpacked_reconstruct(
        df,
        differentia_bitwidth=differentia_bitwidth,
        dstream_S=dstream_S,
        exploded_slice_size=exploded_slice_size,
    )
