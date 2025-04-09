import numpy as np
import pandas as pd

from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_is_working_format_asexual import (
    alifestd_is_working_format_asexual,
)
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._jit import jit


@jit(nopython=True)
def _alifestd_calc_clade_trait_count_asexual_fast_path(
    ancestor_ids: np.ndarray,
    trait_mask: np.ndarray,
) -> np.ndarray:
    """Implementation detail for `alifestd_calc_clade_trait_count_asexual`."""

    # iterate over ancestor_ids from back to front
    for idx_r, ancestor_id in enumerate(ancestor_ids[::-1]):
        idx = len(ancestor_ids) - 1 - idx_r
        if ancestor_id == idx:
            continue  # handle genesis cases

        trait_mask[ancestor_id] += trait_mask[idx]

    return trait_mask


def _alifestd_calc_clade_trait_count_asexual_slow_path(
    phylogeny_df: pd.DataFrame,
) -> pd.DataFrame:
    """Implementation detail for `alifestd_calc_clade_trait_count_asexual`."""

    saved_id_order = None
    if not alifestd_is_topologically_sorted(phylogeny_df):
        saved_id_order = phylogeny_df["id"].to_numpy(copy=True)
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

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

    if alifestd_is_working_format_asexual(phylogeny_df):
        return _alifestd_calc_clade_trait_count_asexual_fast_path(
            phylogeny_df["ancestor_id"].to_numpy(dtype=int),
            phylogeny_df["alifestd_calc_trait_count_asexual"].to_numpy(),
        )
    else:
        return _alifestd_calc_clade_trait_count_asexual_slow_path(phylogeny_df)
