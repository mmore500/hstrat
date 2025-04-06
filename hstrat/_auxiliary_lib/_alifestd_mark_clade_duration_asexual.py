import pandas as pd

from ._alifestd_mark_max_descendant_origin_time_asexual import (
    alifestd_mark_max_descendant_origin_time_asexual,
)


def alifestd_mark_clade_duration_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `clade_duration`, containing the difference between each the
    `origin_time` of each node and the maximum `origin_time` of its descendants.

    Leaf nodes will have duration 0.

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

    phylogeny_df["clade_duration"] = (
        phylogeny_df["max_descendant_origin_time"].values
        - phylogeny_df["origin_time"].values
    )

    return phylogeny_df
