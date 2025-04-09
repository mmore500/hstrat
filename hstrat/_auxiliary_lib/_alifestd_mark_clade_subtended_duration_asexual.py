import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_mark_max_descendant_origin_time_asexual import (
    alifestd_mark_max_descendant_origin_time_asexual,
)


def alifestd_mark_clade_subtended_duration_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `clade_subtended_duration`, containing the difference between each the
    `origin_time` of each node's ancestor and the maximum
    `origin_time` of its descendants.

    Ancestor origin time for root nodes will be 0.

    Dataframe reindexing (e.g., df.index) may be applied.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if "origin_time" not in phylogeny_df.columns:
        raise ValueError("phylogeny_df must contain `origin_time` column")

    if "max_descendant_origin_time" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_max_descendant_origin_time_asexual(
            phylogeny_df, mutate=True
        )

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    ancestor_origin_times = np.where(
        phylogeny_df["ancestor_id"].values != phylogeny_df["id"].values,
        phylogeny_df.loc[
            phylogeny_df["ancestor_id"].values, "origin_time"
        ].values,
        0,
    )

    phylogeny_df["clade_subtended_duration"] = (
        phylogeny_df["max_descendant_origin_time"].values
        - ancestor_origin_times
    )

    return phylogeny_df
