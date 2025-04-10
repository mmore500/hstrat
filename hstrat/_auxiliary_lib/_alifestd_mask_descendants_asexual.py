import numpy as np
import pandas as pd

from hstrat._auxiliary_lib import (
    alifestd_has_contiguous_ids,
    alifestd_is_topologically_sorted,
    alifestd_topological_sort,
    alifestd_try_add_ancestor_id_col,
)


def alifestd_mask_descendants_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    *,
    ancestor_mask: np.ndarray,
) -> pd.DataFrame:
    """For given ancestor nodes, create a mask identifying those nodes and all
    descendants.

    Ancestral nodes are identified by `ancestor_mask` corresponding to rows
    in `phylogeny_df`.

    The mask is returned as a new column `alifestd_mask_descendants_asexual` in
    the output DataFrame.

    A topological sort will be applied if `phylogeny_df` is not topologically
    sorted. Dataframe reindexing (e.g., df.index) may be applied.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    phylogeny_df["alifestd_mask_descendants_asexual"] = ancestor_mask

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    for idx in phylogeny_df.index:
        ancestor_id = phylogeny_df.at[idx, "ancestor_id"]

        phylogeny_df.at[idx, "alifestd_mask_descendants_asexual"] = (
            phylogeny_df.at[ancestor_id, "alifestd_mask_descendants_asexual"]
            | phylogeny_df.at[idx, "alifestd_mask_descendants_asexual"]
        )

    return phylogeny_df
