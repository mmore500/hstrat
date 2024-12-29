import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_mark_node_depth_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `node_depth`, counting the number of nodes between a node
    and the root.

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

    phylogeny_df["node_depth"] = -1

    for idx in phylogeny_df.index:
        ancestor_id = phylogeny_df.loc[idx, "ancestor_id"]
        ancestor_depth = phylogeny_df.loc[ancestor_id, "node_depth"]
        phylogeny_df.loc[idx, "node_depth"] = ancestor_depth + 1

    return phylogeny_df
