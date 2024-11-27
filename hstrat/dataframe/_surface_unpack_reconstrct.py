import logging
from copy import deepcopy

import tqdm
from downstream import dataframe as dstream_dataframe
import polars as pl
import numpy as np

from .._auxiliary_lib import alifestd_make_empty
from ..phylogenetic_inference.tree.build_tree_searchtable_cpp import (
    build as build_cpp,
)
from ..phylogenetic_inference.tree._build_tree_searchtable import (
    finalize_records_cpp,
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

    num_rows = df.lazy().select(pl.len()).collect().item()
    with pl.Config() as cfg:
        cfg.set_tbl_cols(df.lazy().collect_schema().len())
        head = repr(df.lazy().head().collect())
        message = " ".join(["packed df:", str(num_rows), "rows\n", head])
        logging.info(message)

    # for simplicity, return early for this special case
    if num_rows == 0:
        return pl.from_pandas(alifestd_make_empty())

    df = dstream_dataframe.unpack_data_packed(df)
    with pl.Config() as cfg:
        cfg.set_tbl_cols(df.lazy().collect_schema().len())
        head = repr(df.lazy().head().collect())
        message = " ".join(["unpacked df:", str(num_rows), "rows\n", head])
        logging.info(message)

    long_df = dstream_dataframe.explode_lookup_unpacked(
        df, value_type="uint64"
    )
    with pl.Config() as cfg:
        cfg.set_tbl_cols(long_df.lazy().collect_schema().len())
        head = repr(long_df.lazy().head().collect())
        message = " ".join(["exploded df:", str(num_rows), "rows\n", head])
        logging.info(message)

    logging.info("building tree...")
    records = build_cpp(
        long_df["dstream_data_id"].to_numpy(),
        long_df["dstream_T"].to_numpy(),
        long_df["dstream_Tbar"].to_numpy(),
        long_df["dstream_value"].to_numpy(),
        tqdm.tqdm(total=len(df)),
    )

    logging.info("finalizing tree...")
    phylo_df = pl.from_pandas(
        pl.from_dict(
            {  # type: ignore
                "dstream_data_id": np.frombuffer(
                    records.dstream_data_id, dtype=np.uint64
                ),
                "id": np.frombuffer(records.id, dtype=np.uint64),
                "ancestor_id": np.frombuffer(
                    records.ancestor_id, dtype=np.uint64
                ),
                "rank": np.frombuffer(records.rank, dtype=np.uint64),
                "differentia": np.frombuffer(
                    records.differentia, dtype=np.uint64
                ),
            },
            schema={
                "dstream_data_id": pl.UInt64,
                "id": pl.UInt64,
                "ancestor_id": pl.UInt64,
                "differentia": pl.UInt64,
                "rank": pl.UInt64,
            },
        ).to_pandas()
    )  # fastest found method of copying memoryview from records object

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
    with pl.Config() as cfg:
        cfg.set_tbl_cols(phylo_df.lazy().collect_schema().len())
        cfg.set_tbl_cols(phylo_df.width)
        head = repr(phylo_df.lazy().head(10).collect())
        message = " ".join(["reconst df:", str(num_rows), "rows\n", head])
        logging.info(message)

    return phylo_df
