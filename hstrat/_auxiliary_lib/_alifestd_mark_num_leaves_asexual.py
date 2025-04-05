import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_mark_num_leaves_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `num_leaves` with count of all descendant leaves, including
    self if a leaf.

    A topological sort will be applied if `phylogeny_df` is not topologically
    sorted. Dataframe reindexing (e.g., df.index) may be applied.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    phylogeny_df["num_leaves"] = 0

    for idx in reversed(phylogeny_df.index):
        ancestor_id = phylogeny_df.loc[idx, "ancestor_id"]

        if phylogeny_df.loc[idx, "num_leaves"] == 0:
            phylogeny_df.loc[idx, "num_leaves"] = 1

        delta = phylogeny_df.loc[idx, "num_leaves"]
        if ancestor_id != idx:  # exclude genesis case
            phylogeny_df.loc[ancestor_id, "num_leaves"] += delta

    return phylogeny_df
