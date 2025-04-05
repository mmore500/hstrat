import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_strictly_bifurcating_asexual import (
    alifestd_is_strictly_bifurcating_asexual,
)
from ._alifestd_mark_right_child_asexual import (
    alifestd_mark_right_child_asexual,
)
from ._alifestd_mark_roots import alifestd_mark_roots
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_mark_is_right_child_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `is_right_child`, containing for each node whether it is the
    larger-id child.

    Root nodes will be marked False. Tree must be strictly bifurcating.

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

    if "right_child" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_right_child_asexual(
            phylogeny_df, mutate=True
        )

    if "is_root" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_roots(phylogeny_df, mutate=True)

    phylogeny_df["is_right_child"] = (
        phylogeny_df.loc[phylogeny_df["ancestor_id"], "right_child"].values
        == phylogeny_df["id"].values
    ) & ~phylogeny_df["is_root"].values

    return phylogeny_df
