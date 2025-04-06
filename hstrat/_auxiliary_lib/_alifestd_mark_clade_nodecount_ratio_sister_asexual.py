import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_strictly_bifurcating_asexual import (
    alifestd_is_strictly_bifurcating_asexual,
)
from ._alifestd_mark_num_descendants_asexual import (
    alifestd_mark_num_descendants_asexual,
)
from ._alifestd_mark_sister_asexual import alifestd_mark_sister_asexual


def alifestd_mark_clade_nodecount_ratio_sister_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `clade_nodecount_ratio_sister`, containing the ratio of each
    clade size to that of its sister.

    Root nodes will have ratio 1. Tree must be strictly bifurcating.

    Dataframe reindexing (e.g., df.index) may be applied.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if not alifestd_is_strictly_bifurcating_asexual(phylogeny_df):
        raise ValueError("phylogeny_df must be strictly bifurcating")

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    if "sister" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_sister_asexual(phylogeny_df, mutate=True)

    if "num_descendants" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_num_descendants_asexual(
            phylogeny_df, mutate=True
        )

    phylogeny_df["clade_nodecount_ratio_sister"] = (
        phylogeny_df["num_descendants"] + 1
    ) / (
        phylogeny_df.loc[phylogeny_df["sister"], "num_descendants"].values + 1
    )

    return phylogeny_df
