import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_strictly_bifurcating_asexual import (
    alifestd_is_strictly_bifurcating_asexual,
)
from ._alifestd_mark_is_left_child_asexual import (
    alifestd_mark_is_left_child_asexual,
)
from ._alifestd_mark_is_right_child_asexual import (
    alifestd_mark_is_right_child_asexual,
)
from ._alifestd_mark_left_child_asexual import alifestd_mark_left_child_asexual
from ._alifestd_mark_right_child_asexual import (
    alifestd_mark_right_child_asexual,
)
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_mark_sister_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `sister`, containing the id of each node's sibling.

    Root nodes will be marked with their own id. Phylogeny must be
    strictly bifurcating.

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

    if "left_child_id" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_left_child_asexual(
            phylogeny_df, mutate=True
        )
    if "right_child_id" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_right_child_asexual(
            phylogeny_df, mutate=True
        )
    if "is_left_child" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_is_left_child_asexual(
            phylogeny_df, mutate=True
        )
    if "is_right_child" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_is_right_child_asexual(
            phylogeny_df, mutate=True
        )

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    phylogeny_df["sister_id"] = (
        phylogeny_df.loc[phylogeny_df["ancestor_id"], "right_child_id"].values
        * phylogeny_df["is_left_child"].values
        + phylogeny_df.loc[phylogeny_df["ancestor_id"], "left_child_id"].values
        * phylogeny_df["is_right_child"].values
        + phylogeny_df["id"].values
        * (phylogeny_df["ancestor_id"].values == phylogeny_df["id"].values)
    )

    return phylogeny_df
