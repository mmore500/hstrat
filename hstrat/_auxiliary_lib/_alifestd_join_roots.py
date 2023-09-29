import pandas as pd

from ._alifestd_mark_roots import alifestd_mark_roots


def alifestd_join_roots(
    phylogeny_df: pd.DataFrame, mutate: bool = False
) -> pd.DataFrame:
    """Point all other roots to oldest root, measured by lowest `origin_time`
    (if available) or otherwise lowest `id`.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_mark_roots(phylogeny_df, mutate=True)
    if len(phylogeny_df) <= 1:
        return phylogeny_df

    phylogeny_df.reset_index(drop=True, inplace=True)
    idxmin: int
    if "origin_time" in phylogeny_df.columns:
        idxmin = (
            phylogeny_df.loc[phylogeny_df["is_root"]]
            .sort_values(by=["origin_time", "id"])
            .index[0]
        )
    else:
        idxmin = phylogeny_df.loc[phylogeny_df["is_root"], "id"].idxmin()

    global_root_id = phylogeny_df.loc[idxmin, "id"]

    if "ancestor_id" in phylogeny_df:
        phylogeny_df.loc[
            phylogeny_df["is_root"], "ancestor_id"
        ] = global_root_id

    phylogeny_df.loc[
        phylogeny_df["is_root"], "ancestor_list"
    ] = f"[{global_root_id}]"
    phylogeny_df["is_root"] = False

    phylogeny_df.loc[idxmin, "ancestor_list"] = "[none]"
    phylogeny_df.loc[idxmin, "is_root"] = True

    return phylogeny_df
