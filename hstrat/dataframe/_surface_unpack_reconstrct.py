import logging
import sys

from downstream import dataframe as dstream_dataframe
import numpy as np
import polars as pl
from tqdm import tqdm

from .._auxiliary_lib import alifestd_make_empty
from ..phylogenetic_inference.tree._build_tree_searchtable import (
    Record,
    finalize_records,
    insert_artifact,
)


def surface_unpack_reconstruct(df: pl.DataFrame) -> pl.DataFrame:
    """Unpack dstream buffer and counter from genome data and construct an
    estimated phylogenetic tree for the genomes.

    Parameters
    ----------
    df : pl.DataFrame
        The input DataFrame containing packed data with required columns, one
        row per dstream buffer.

        Required schema:
            - 'data_hex' : pl.String
                - Raw binary data, with serialized dstream buffer and counter.
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

    Returns
    -------
    pl.DataFrame
        The output DataFrame containing the estimated phylogenetic tree in
        alife standard format, with the following columns:

        - 'taxon_id' : pl.UInt64
            - Unique identifier for each taxon.
        - 'taxon_label' : pl.String
            - Name of taxon.
        - 'ancestor_id' : pl.UInt64
            - Unique identifier for ancestor taxon.
        - 'ancestor_list' : str
            - List of ancestor taxon identifiers.
        - 'origin_time' : pl.Float64
            - Estimated origin time of phylogeny nodes.
        - 'dstream_T_bitwidth' : pl.UInt64
            - Size of annotation differentiae, in bits.
        - 'dstream_data_id' : pl.UInt64
            - Unique identifier for each data item.
        - 'dstream_T' : pl.UInt64
            - Num generations elapsed for tip taxon.
        - 'dstream_Tbar' : pl.Float64
            - Num generations elapsed for ancestral differentia.
        - 'dstream_data_id' : pl.UInt64
            - Unique identifier for each data item.

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
    # TODO pass whole columns to c++ implementation
    records = [Record(taxon_label=sys.maxsize)]
    for frame in tqdm(long_df.iter_slices(64), total=len(long_df) // 64):
        insert_artifact(
            records,
            frame["dstream_Tbar"],
            frame["dstream_value"],
            frame["dstream_data_id"].first(),
            frame["dstream_T"].first(),
        )

    logging.info("finalizing tree...")
    phylo_df = finalize_records(records, force_common_ancestry=True)
    phylo_df["dstream_data_id"] = phylo_df["data_id"].astype(np.uint64)

    logging.info("joining frames...")
    phylo_df = pl.from_pandas(phylo_df)
    res = phylo_df.join(
        df.select(pl.exclude("^dstream_*$", "^downstream_*$")).cast(
            {"dstream_data_id": pl.UInt64},
        ),
        on="dstream_data_id",
        how="left",
    )

    logging.info("surface_unpack_reconstruct complete")
    with pl.Config() as cfg:
        cfg.set_tbl_cols(phylo_df.lazy().collect_schema().len())
        cfg.set_tbl_cols(phylo_df.width)
        head = repr(phylo_df.lazy().head().collect())
        message = " ".join(["reconst df:", str(num_rows), "rows\n", head])
        logging.info(message)

    return res
