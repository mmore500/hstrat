import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_strictly_bifurcating_asexual import (
    alifestd_is_strictly_bifurcating_asexual,
)
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_mark_right_child_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `right_child`, containing for each node its largest-id child.

    Leaf nodes will be marked with their own id.

    Dataframe reindexing (e.g., df.index) may be applied.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if not alifestd_is_strictly_bifurcating_asexual(phylogeny_df):
        raise ValueError("phylogeny_df must be strictly bifurcating")

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    phylogeny_df["right_child"] = phylogeny_df["id"]

    for idx in phylogeny_df.index:
        ancestor_id = phylogeny_df.loc[idx, "ancestor_id"]
        if ancestor_id == idx:
            continue  # handle genesis cases

        cur_right_child = phylogeny_df.loc[ancestor_id, "right_child"]
        if cur_right_child == ancestor_id or idx > cur_right_child:
            phylogeny_df.loc[ancestor_id, "right_child"] = idx

    return phylogeny_df
