import pandas as pd

from ._alifestd_find_leaf_ids import alifestd_find_leaf_ids
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids


def alifestd_mark_leaves(
    phylogeny_df: pd.DataFrame, mutate: bool = False
) -> pd.DataFrame:
    """What rows are ancestor to no other row?

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    leaf_ids = alifestd_find_leaf_ids(phylogeny_df)
    phylogeny_df["is_leaf"] = False
    phylogeny_df.loc[leaf_ids, "is_leaf"] = True

    return phylogeny_df
