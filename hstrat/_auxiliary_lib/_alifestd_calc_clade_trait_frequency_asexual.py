import numpy as np
import pandas as pd

from ._alifestd_calc_clade_trait_count_asexual import (
    alifestd_calc_clade_trait_count_asexual,
)


def alifestd_calc_clade_trait_frequency_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    *,
    mask_trait_absent: np.ndarray,  # 1D boolean array
    mask_trait_present: np.ndarray,  # 1D boolean array
) -> np.ndarray:
    """Calculate what fraction of nodes within each clade have a given trait.

    Clades are defined as a node and all descendant nodes. The
    `mask_trait_absent` parameter can be used to exclude nodes from
    consideration, for instance &'ing with `alifestd_mark_leaves` can be used
    to only consider trait frequency among descendant leaves.

    Returns a numpy array of the same length as the input DataFrame, with array
    elements as the number of nodes in the clade that have the trait. Returned
    array matches row order of the input DataFrame.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    mask_trait_absent = np.asarray(mask_trait_absent, dtype=bool)
    mask_trait_present = np.asarray(mask_trait_present, dtype=bool)

    if np.any(mask_trait_absent & mask_trait_present):
        raise ValueError(
            "mask_trait_absent and mask_trait_present not mutually exclusive",
        )

    trait_count_absent = alifestd_calc_clade_trait_count_asexual(
        phylogeny_df,
        mutate=True,
        trait_mask=mask_trait_absent,
    )
    trait_count_present = alifestd_calc_clade_trait_count_asexual(
        phylogeny_df,
        mutate=True,
        trait_mask=mask_trait_present,
    )

    return trait_count_present / (
        trait_count_present + trait_count_absent
    )  # numpy division implicitly converts to float
