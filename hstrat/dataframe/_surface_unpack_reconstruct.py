import logging
import math

from downstream import dataframe as dstream_dataframe
import polars as pl
import tqdm

from .._auxiliary_lib import (
    alifestd_make_empty,
    log_context_duration,
    render_polars_snapshot,
)
from ..phylogenetic_inference.tree._impl._build_tree_searchtable_cpp_impl_stub import (
    Records,
    collapse_dropped_unifurcations,
    extend_tree_searchtable_cpp_from_exploded,
    records_to_dict,
)


def _get_sole_bitwidth(df: pl.DataFrame) -> int:
    """Get dstream bitwidth value from DataFrame, ensuring it is unique."""
    assert not df.lazy().limit(1).collect().is_empty()
    if (
        not df.lazy()
        .filter(pl.col("dstream_value_bitwidth").diff() != pl.lit(0))
        .limit(1)
        .collect()
        .is_empty()
    ):
        raise NotImplementedError(
            "multiple differentia_bitwidths not yet supported",
        )
    return df.lazy().select("dstream_value_bitwidth").limit(1).collect().item()


def _build_records_chunked(
    df: pl.DataFrame, exploded_slice_size: int
) -> Records:
    """Build tree searchtable from DataFrame, exploding in chunks to reduce
    memory usage."""
    num_slices = math.ceil(len(df) / exploded_slice_size)
    logging.info(f"{len(df)=} {exploded_slice_size=} {num_slices=}")

    init_size = len(df) * df["dstream_S"].first()
    records = Records(init_size)
    for i, df_slice in enumerate(df.iter_slices(exploded_slice_size)):
        logging.info(f"incorporating slice {i}/{num_slices}...")

        with log_context_duration(
            f"explode dstream records, slice {i}", logging.info
        ):
            long_df = dstream_dataframe.explode_lookup_unpacked(
                df_slice, value_type="uint64"
            )

        if i == 0:
            render_polars_snapshot(long_df, "exploded", logging.info)

        with log_context_duration(f"build tree, slice {i}", logging.info):
            extend_tree_searchtable_cpp_from_exploded(
                records,
                long_df["dstream_data_id"].to_numpy(),
                long_df["dstream_T"].to_numpy(),
                long_df["dstream_Tbar"].to_numpy(),
                long_df["dstream_value"].to_numpy(),
                tqdm.tqdm,
            )

        with log_context_duration(
            f"collapse dropped unifurcations, slice {i}", logging.info
        ):
            records = collapse_dropped_unifurcations(records)

    return records


def surface_unpack_reconstruct(
    df: pl.DataFrame,
    exploded_slice_size=10_000_000,
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

    exploded_slice_size : int, default 10_000_000
        Number of rows to process at once. Lower values reduce memory usage.

    Returns
    -------
    pl.DataFrame
        The output DataFrame containing the estimated phylogenetic tree in
        alife standard format, with the following columns:

        - 'taxon_id' : pl.UInt64
            - Unique identifier for each taxon (RE alife standard format).
        - 'ancestor_id' : pl.UInt64
            - Unique identifier for ancestor taxon  (RE alife standard format).
        - 'origin_tme' : pl.UInt64
            - Num generations elapsed for ancestral differentia.
            - RE alife standard format.
            - a.k.a. "rank"
                - Corresponds to`dstream_Tbar` for inner nodes.
                - Corresponds `dstream_T` - 1 for leaf nodes
        - 'differentia_bitwidth' : pl.UInt64
            - Size of annotation differentiae, in bits.
            - Corresponds to `dstream_value_bitwidth`.
        - 'dstream_data_id' : pl.UInt64
            - Unique identifier for each genome in source dataframe
            - Set to source dataframe row index if not provided.

        User-defined columns, except some prefixed with 'downstream_' or
        'dstream_', will be forwarded from the input DataFrame.

        Note that the alife-standard `ancestor_list` column is not included in
        the output.
    """
    render_polars_snapshot(df, "packed", logging.info)

    # for simplicity, return early for this special case
    if df.lazy().limit(1).collect().is_empty():
        logging.info("empty input dataframe, returning empty result")
        return pl.from_pandas(alifestd_make_empty())

    logging.info("extracting differentia bitwidth...")
    df = df.with_columns(
        dstream_value_bitwidth=(
            pl.col("dstream_storage_bitwidth") // pl.col("dstream_S")
        ),
    )
    differentia_bitwidth = _get_sole_bitwidth(df)
    logging.info(f" - differentia bitwidth: {differentia_bitwidth}")

    with log_context_duration("unpack genome strings", logging.info):
        df = dstream_dataframe.unpack_data_packed(df)
    render_polars_snapshot(df, "unpacked", logging.info)

    logging.info("building tree searchtable chunkwise...")
    records = _build_records_chunked(df, exploded_slice_size)

    logging.info("converting records to dict...")
    records_dict = records_to_dict(records)

    logging.info("finalizing phylogeny dataframe...")

    phylo_df = pl.from_dict(
        records_dict,  # type: ignore
        schema={
            "dstream_data_id": pl.UInt64,
            "id": pl.UInt64,
            "ancestor_id": pl.UInt64,
            "differentia": pl.UInt64,
            "rank": pl.UInt64,
        },
    )
    del records
    phylo_df = phylo_df.with_columns(
        pl.lit(differentia_bitwidth)
        .alias("differentia_bitwidth")
        .cast(pl.UInt32),
    )

    logging.info("joining user-defined columns...")
    with log_context_duration("join user-defined columns", logging.info):
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

    logging.info("surface_unpack_reconstruct complete")
    render_polars_snapshot(phylo_df, "reconstruction", logging.info)

    return phylo_df
