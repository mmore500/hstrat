import pandas as pd

from ._alifestd_make_ancestor_list_col import alifestd_make_ancestor_list_col
from ._alifestd_mark_leaves import alifestd_mark_leaves
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_add_inner_knuckles_asexual(
    phylogeny_df: pd.DataFrame, mutate: bool = False
) -> pd.DataFrame:
    """For all inner nodes, add a subtending unifurcation ("knuckle").

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_mark_leaves(phylogeny_df, mutate=True)

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)
    if "ancestor_id" not in phylogeny_df:
        raise ValueError("asexual phylogeny required")

    inner_df = phylogeny_df[~phylogeny_df["is_leaf"]].copy()

    if inner_df.empty:
        return phylogeny_df

    if "is_root" in inner_df:
        inner_df["is_root"] = False

    if "origin_time_delta" in inner_df:
        inner_df["origin_time_delta"] = 0

    id_delta = phylogeny_df["id"].max() + 1

    inner_df["ancestor_id"] += id_delta * (
        inner_df["id"] == inner_df["ancestor_id"]
    )
    inner_df["id"] += id_delta

    if not (inner_df["id"].min() > phylogeny_df["id"].max()):
        raise ValueError("overflow in new id assigment")

    phylogeny_df.loc[~phylogeny_df["is_leaf"], "ancestor_id"] = (
        phylogeny_df.loc[~phylogeny_df["is_leaf"], "id"] + id_delta
    )

    res = pd.concat([phylogeny_df, inner_df], ignore_index=True)

    if "ancestor_list" in res:
        res["ancestor_list"] = alifestd_make_ancestor_list_col(
            res["id"],
            res["ancestor_id"],
        )

    return res
