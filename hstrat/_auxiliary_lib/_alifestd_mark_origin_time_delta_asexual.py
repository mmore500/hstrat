import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_mark_origin_time_delta_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add columns `origin_time_delta` and `origin_time_ancestor`.

    Dataframe must provide column `origin_time`.

    A topological sort will be applied if `phylogeny_df` is not topologically
    sorted. Reindexing may be applied.

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

    phylogeny_df["origin_time_ancestor"] = 0

    for idx in reversed(phylogeny_df.index):
        ancestor_id = phylogeny_df.loc[idx, "ancestor_id"]
        ancestor_origin_time = phylogeny_df.loc[ancestor_id, "origin_time"]
        phylogeny_df.loc[idx, "origin_time_ancestor"] = ancestor_origin_time

    phylogeny_df["origin_time_delta"] = (
        phylogeny_df["origin_time"] - phylogeny_df["origin_time_ancestor"]
    )

    return phylogeny_df
