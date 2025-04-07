import numpy as np
import pandas as pd

from ._alifestd_calc_clade_trait_frequency_asexual import (
    alifestd_calc_clade_trait_frequency_asexual,
)
from ._alifestd_is_strictly_bifurcating_asexual import (
    alifestd_is_strictly_bifurcating_asexual,
)
from ._alifestd_mark_sister_asexual import alifestd_mark_sister_asexual
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_screen_trait_defined_clades_naive_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    *,
    mask_trait_absent: np.ndarray,  # 1D boolean array
    mask_trait_present: np.ndarray,  # 1D boolean array
    defining_mut_thresh: float = 0.75,
    defining_mut_sister_thresh: float = 0.75,
) -> np.ndarray:  # 1D boolean array
    """Perform a naive screen for trait-defined clades.

    This function checks if the trait frequency in a clade is above a certain
    threshold (`defining_mut_thresh`), and if the trait frequency in the sister
    clade is below a certain threshold (`defining_mut_sister_thresh`). Clades
    are defined as a node and all descendant nodes.

    The `mask_trait_absent` parameter can be used to exclude nodes from
    consideration, for instance &'ing with `alifestd_mark_leaves` can be used
    to only consider trait frequency among descendant leaves.

    Returns a numpy array of bool with the same length as the input DataFrame,
    with array elements as the number of nodes in the clade that have the
    trait. Returned array matches row order of the input DataFrame.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if not alifestd_is_strictly_bifurcating_asexual(phylogeny_df):
        raise ValueError("phylogeny_df must be strictly bifurcating")

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if "sister_id" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_sister_asexual(phylogeny_df, mutate=True)

    trait_frequency = alifestd_calc_clade_trait_frequency_asexual(
        phylogeny_df,
        mutate=True,
        mask_trait_absent=mask_trait_absent,
        mask_trait_present=mask_trait_present,
    )

    phylogeny_df[
        "alifestd_screen_trait_defined_clades_naive_asexual"
    ] = trait_frequency

    sister = phylogeny_df["sister_id"].values
    return (
        phylogeny_df[
            "alifestd_screen_trait_defined_clades_naive_asexual"
        ].values
        >= defining_mut_thresh
    ) & (
        phylogeny_df.loc[
            sister, "alifestd_screen_trait_defined_clades_naive_asexual"
        ].values
        <= defining_mut_sister_thresh
    )
