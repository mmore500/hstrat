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
    """Unpack dstream buffer and counter from genome data  serialized into a single hexadecimal data field, TODO."""

    # for simplicity, return early for this special case
    if len(df.lazy().limit(1).collect()) == 0:
        return pl.from_pandas(alifestd_make_empty())

    df = dstream_dataframe.unpack_data_packed(df)
    long_df = dstream_dataframe.explode_lookup_unpacked(
        df, value_type="uint64"
    )

    group_keys = [*map(pl.col, ("dstream_T", "data_id", "dstream_Tbar"))]
    sorted_df = long_df.lazy().sort(group_keys)

    records = [Record(taxon_label=sys.maxsize)]
    for (dstream_T, data_id, _dstream_Tbar), group_df in tqdm(
        sorted_df.collect().group_by(
            group_keys,
            maintain_order=True,
        ),
    ):
        insert_artifact(
            records,
            # map int to make invariant to numpy input (?)
            group_df["dstream_Tbar"].to_list(),
            group_df["dstream_value"].to_list(),
            data_id,  # TODO ensure data_id is sequential from downstream
            dstream_T,
        )

    phylo_df = finalize_records(records, force_common_ancestry=True)
    phylo_df["data_id"] = phylo_df["data_id"].astype(np.uint64)
    phylo_df = pl.from_pandas(phylo_df)
    return phylo_df.join(df, on="data_id", how="left")
