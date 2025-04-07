import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_calc_clade_trait_count_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    *,
    trait_mask: np.ndarray,  # 1D boolean array
) -> np.ndarray:
    """Count how many nodes within each clade have a given trait.

    Clades are defined as a node and all descendant nodes.

    Returns a numpy array of the same length as the input DataFrame, with array
    elements as the number of nodes in the clade that have the trait. Returned
    array matches row order of the input DataFrame.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df["alifestd_calc_trait_count_asexual"] = np.asarray(
        trait_mask, dtype=int
    )
    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    saved_id_order = None
    if not alifestd_is_topologically_sorted(phylogeny_df):
        saved_id_order = phylogeny_df["id"].to_numpy(copy=True)
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    for idx in reversed(phylogeny_df.index):
        ancestor_id = phylogeny_df.at[idx, "ancestor_id"]
        if ancestor_id == idx:
            continue  # handle genesis cases

        phylogeny_df.at[
            ancestor_id, "alifestd_calc_trait_count_asexual"
        ] += phylogeny_df.at[idx, "alifestd_calc_trait_count_asexual"]

    if saved_id_order is not None:
        return phylogeny_df.loc[
            saved_id_order, "alifestd_calc_trait_count_asexual"
        ].to_numpy()
    else:
        return phylogeny_df["alifestd_calc_trait_count_asexual"].to_numpy()
