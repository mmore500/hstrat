import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_mark_oldest_root import alifestd_mark_oldest_root
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_collapse_trunk_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Collapse entries masked by `is_trunk` column, keeping only the oldest
    root.

    Masked entries must be contiguous, meaning that no non-trunk entry can
    be an ancestor of a trunk entry.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.

    See Also
    --------
    alifestd_delete_trunk_asexual
    """
    if "is_trunk" not in phylogeny_df:
        raise ValueError(
            "`is_trunk` column not provided, trunk is unspecified"
        )

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    phylogeny_df["ancestor_is_trunk"] = phylogeny_df.loc[
        phylogeny_df["ancestor_id"], "is_trunk"
    ].to_numpy()

    if np.any(phylogeny_df["is_trunk"] & ~phylogeny_df["ancestor_is_trunk"]):
        raise ValueError("specified trunk is non-contiguous")

    if phylogeny_df["is_trunk"].sum() <= 1:
        return phylogeny_df

    trunk_df = phylogeny_df.loc[phylogeny_df["is_trunk"]].copy()
    trunk_df = alifestd_mark_oldest_root(trunk_df, mutate=True)
    collapsed_root_id = trunk_df.loc[trunk_df["is_oldest_root"].idxmax(), "id"]
    del trunk_df

    if "ancestor_id" in phylogeny_df:
        phylogeny_df.loc[
            phylogeny_df["ancestor_is_trunk"], "ancestor_id"
        ] = collapsed_root_id

    if "ancestor_list" in phylogeny_df:
        phylogeny_df.loc[
            phylogeny_df["ancestor_is_trunk"], "ancestor_list"
        ] = f"[{collapsed_root_id}]"
        phylogeny_df.loc[collapsed_root_id, "ancestor_list"] = "[none]"

    res = phylogeny_df.loc[
        ~phylogeny_df["is_trunk"] | (phylogeny_df["id"] == collapsed_root_id)
    ].reset_index(drop=True)

    assert res["is_trunk"].sum() <= 1
    return res
