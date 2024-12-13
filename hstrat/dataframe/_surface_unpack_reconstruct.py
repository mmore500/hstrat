import logging

from downstream import dataframe as dstream_dataframe
import polars as pl
import tqdm

from .._auxiliary_lib import (
    alifestd_make_empty,
    alifestd_try_add_ancestor_list_col,
    render_polars_snapshot,
)
from ..phylogenetic_inference.tree._impl._build_tree_searchtable_cpp_impl_stub import (
    build_tree_searchtable_cpp_from_exploded,
)


def surface_unpack_reconstruct(df: pl.DataFrame) -> pl.DataFrame:
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

    Returns
    -------
    pl.DataFrame
        The output DataFrame containing the estimated phylogenetic tree in
        alife standard format, with the following columns:

        - 'taxon_id' : pl.UInt64
            - Unique identifier for each taxon (RE alife standard format).
        - 'ancestor_id' : pl.UInt64
            - Unique identifier for ancestor taxon  (RE alife standard format).
        - 'ancestor_list' : str
            - List of ancestor taxon identifiers (RE alife standard format).
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
    """
    render_polars_snapshot(df, "packed", logging.info)

    # for simplicity, return early for this special case
    if df.lazy().limit(1).collect().is_empty():
        logging.info("empty input dataframe, returning empty result")
        return pl.from_pandas(alifestd_make_empty())

    df = dstream_dataframe.unpack_data_packed(df)
    render_polars_snapshot(df, "unpacked", logging.info)

    long_df = dstream_dataframe.explode_lookup_unpacked(
        df, value_type="uint64"
    )
    render_polars_snapshot(long_df, "exploded", logging.info)

    logging.info("building tree...")
    records = build_tree_searchtable_cpp_from_exploded(
        long_df["dstream_data_id"].to_numpy(),
        long_df["dstream_T"].to_numpy(),
        long_df["dstream_Tbar"].to_numpy(),
        long_df["dstream_value"].to_numpy(),
        tqdm.tqdm,
    )

    logging.info("finalizing tree...")

    phylo_df = pl.from_dict(
        records,  # type: ignore
        schema={
            "dstream_data_id": pl.UInt64,
            "id": pl.UInt64,
            "ancestor_id": pl.UInt64,
            "differentia": pl.UInt64,
            "rank": pl.UInt64,
        },
    )

    logging.info("adding ancestor list column...")
    phylo_df = alifestd_try_add_ancestor_list_col(phylo_df)

    logging.info("joining frames...")
    df = df.select(
        pl.exclude("^dstream_.*$", "^downstream_.*$"),
        pl.col("dstream_data_id").cast(pl.UInt64),
    )
    phylo_df = phylo_df.join(df, on="dstream_data_id", how="left")
    bitwidths = (
        long_df.lazy().select("dstream_value_bitwidth").unique().limit(2)
    ).collect()
    if len(bitwidths) > 1:
        raise NotImplementedError(
            "multiple differentia_bitwidths not yet supported",
        )
    phylo_df = phylo_df.with_columns(
        pl.lit(bitwidths.item()).alias("differentia_bitwidth").cast(pl.UInt32),
    )

    logging.info("surface_unpack_reconstruct complete")
    render_polars_snapshot(phylo_df, "reconstruction", logging.info)

    return phylo_df
