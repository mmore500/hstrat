from fishersrc import pvalue_npy as fisher_pvalue_npy
import numpy as np
import pandas as pd

from ._alifestd_calc_clade_trait_count_asexual import (
    alifestd_calc_clade_trait_count_asexual,
)
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_strictly_bifurcating_asexual import (
    alifestd_is_strictly_bifurcating_asexual,
)
from ._alifestd_mark_sister_asexual import alifestd_mark_sister_asexual
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_screen_trait_defined_clades_fisher_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    *,
    mask_trait_absent: np.ndarray,  # 1D boolean array
    mask_trait_present: np.ndarray,  # 1D boolean array
) -> np.ndarray:  # 1D float array
    """Perform a screen for trait-defined clades based on Fisher's exact test.

    This function computes a Fisher's exact test comparing the trait frequency
    (number of clade members with the trait, number of clade members without
    the trait) in a clade with its sister clade. Returned values are one-tailed
    p-values for the hypothesis that the trait frequency in the clade is
    greater than in the sister clade.

    Root clades will be compared to themselves, as they have no sister clade.
    As such, root clades will take on p-values > 0.5.

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

    trait_count_absent = alifestd_calc_clade_trait_count_asexual(
        phylogeny_df,
        mutate=True,
        trait_mask=mask_trait_absent,
    ).astype(np.uint32)

    trait_count_present = alifestd_calc_clade_trait_count_asexual(
        phylogeny_df,
        mutate=True,
        trait_mask=mask_trait_present,
    ).astype(np.uint32)

    phylogeny_df[
        "alifestd_screen_trait_defined_clades_fisher_asexual_absent"
    ] = trait_count_absent
    phylogeny_df[
        "alifestd_screen_trait_defined_clades_fisher_asexual_present"
    ] = trait_count_present

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.set_index("id", drop=False, inplace=True)

    sister = phylogeny_df["sister_id"].values
    sister_trait_count_absent = phylogeny_df.loc[
        sister, "alifestd_screen_trait_defined_clades_fisher_asexual_absent"
    ].values
    sister_trait_count_present = phylogeny_df.loc[
        sister, "alifestd_screen_trait_defined_clades_fisher_asexual_present"
    ].values

    return fisher_pvalue_npy(
        a_true=trait_count_present,
        a_false=trait_count_absent,
        b_true=sister_trait_count_present,
        b_false=sister_trait_count_absent,
    )[
        1
    ]  # one-tailed p-value
