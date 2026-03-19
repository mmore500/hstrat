import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_strictly_bifurcating_asexual import (
    alifestd_is_strictly_bifurcating_asexual,
)
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._jit import jit


@jit(nopython=True)
def _alifestd_mark_right_child_asexual_fast_path(
    ancestor_ids: np.ndarray,
) -> np.ndarray:
    """Implementation detail for `alifestd_mark_right_child_asexual`."""

    right_children = np.arange(len(ancestor_ids), dtype=ancestor_ids.dtype)
    for idx, ancestor_id in enumerate(ancestor_ids):
        if ancestor_id == idx:
            continue  # handle genesis cases

        cur_right_child = right_children[ancestor_id]
        if cur_right_child == ancestor_id or idx > cur_right_child:
            right_children[ancestor_id] = idx

    return right_children


def _alifestd_mark_right_child_asexual_slow_path(
    phylogeny_df: pd.DataFrame,
) -> pd.DataFrame:
    """Implementation detail for `alifestd_mark_right_child_asexual`."""

    phylogeny_df.index = phylogeny_df["id"]

    phylogeny_df["right_child_id"] = phylogeny_df["id"]

    for idx in phylogeny_df.index:
        ancestor_id = phylogeny_df.at[idx, "ancestor_id"]
        if ancestor_id == idx:
            continue  # handle genesis cases

        cur_right_child = phylogeny_df.at[ancestor_id, "right_child_id"]
        if cur_right_child == ancestor_id or idx > cur_right_child:
            phylogeny_df.at[ancestor_id, "right_child_id"] = idx

    return phylogeny_df


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
        phylogeny_df[
            "right_child_id"
        ] = _alifestd_mark_right_child_asexual_fast_path(
            phylogeny_df["ancestor_id"].to_numpy()
        )
        return phylogeny_df
    else:
        return _alifestd_mark_right_child_asexual_slow_path(
            phylogeny_df,
        )
