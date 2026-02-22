import numpy as np
import ordered_set as ods
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def _alifestd_find_leaf_ids_asexual_fast_path(
    ancestor_ids: np.ndarray,
) -> np.ndarray:
    child_counts = np.bincount(
        # root is self ref, but must exclude to handle only-root phylo
        ancestor_ids[ancestor_ids != np.arange(len(ancestor_ids))],
        minlength=len(ancestor_ids),
    )
    return np.flatnonzero(child_counts == 0)


def alifestd_find_leaf_ids(phylogeny_df: pd.DataFrame) -> np.ndarray:
    """What ids are not listed in any `ancestor_list`?

    Input dataframe is not mutated by this operation.
    """

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df)
        if "ancestor_id" in phylogeny_df:
            return _alifestd_find_leaf_ids_asexual_fast_path(
                phylogeny_df["ancestor_id"].to_numpy(),
            )

    all_ids = ods.OrderedSet(phylogeny_df["id"])
    internal_ids = (
        set(
            ancestor_id
            for ancestor_list in phylogeny_df["ancestor_list"]
            for ancestor_id in (
                alifestd_parse_ancestor_ids(ancestor_list)
                if isinstance(ancestor_list, str)
                else ancestor_list
            )
        )
        if "ancestor_id" not in phylogeny_df
        else set(
            # root is self ref, but must exclude to handle only-root phylo
            phylogeny_df.loc[
                phylogeny_df["ancestor_id"] != phylogeny_df["id"],
                "ancestor_id",
            ]
        )
    )
    return np.fromiter(all_ids - internal_ids, dtype=int)
