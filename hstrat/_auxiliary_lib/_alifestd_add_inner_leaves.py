import numpy as np
import pandas as pd

from ._alifestd_make_ancestor_list_col import alifestd_make_ancestor_list_col
from ._alifestd_mark_leaves import alifestd_mark_leaves


def alifestd_add_inner_leaves(
    phylogeny_df: pd.DataFrame, mutate: bool = False
) -> pd.DataFrame:
    """Create a zero-length branch with leaf node for each inner node.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_mark_leaves(phylogeny_df, mutate=True)

    inner_df = phylogeny_df[~phylogeny_df["is_leaf"]].copy()
    inner_df["is_leaf"] = True

    if inner_df.empty:
        return phylogeny_df

    if "is_root" in inner_df:
        inner_df["is_root"] = False

    if "origin_time_delta" in inner_df:
        inner_df["origin_time_delta"] = 0

    inner_df["ancestor_id"] = inner_df["id"]

    inner_df["id"] = np.arange(len(inner_df)) + phylogeny_df["id"].max() + 1
    if not (inner_df["id"].min() > phylogeny_df["id"].max()):
        print(inner_df["id"].min(), phylogeny_df["id"].max())
        raise ValueError("overflow in new id assigment")

    if "ancestor_list" in inner_df:
        inner_df["ancestor_list"] = alifestd_make_ancestor_list_col(
            inner_df["id"],
            inner_df["ancestor_id"],
        )

    if "ancestor_id" not in phylogeny_df:
        del inner_df["ancestor_id"]

    return pd.concat([phylogeny_df, inner_df], ignore_index=True)
