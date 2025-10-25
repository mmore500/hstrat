import typing

import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_strictly_bifurcating_asexual import (
    alifestd_is_strictly_bifurcating_asexual,
)
from ._alifestd_mark_node_depth_asexual import alifestd_mark_node_depth_asexual
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_screen_trait_defined_clades_fitch_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    *,
    mask_trait_absent: np.ndarray,  # 1D boolean array
    mask_trait_present: np.ndarray,  # 1D boolean array
    progress_wrap: typing.Callable = lambda x: x,
) -> np.ndarray:  # 1D boolean array
    """Perform a maximum parsimony screen for trait-defined clades using
    Fitch's algorithm.

    The `mask_trait_absent` parameter can be used to exclude nodes from
    consideration, for instance &'ing with `alifestd_mark_leaves` can be used
    to only consider traits on leaves.

    Pass tqdm or equivalent as `progress_wrap` to display a progress bar.

    Default root state is assumed to be False.

    Returns a numpy array of bool with the same length as the input DataFrame,
    with array elements as the number of nodes in the clade that have the
    trait. Returned array matches row order of the input DataFrame.
    """

    if len(phylogeny_df) == 0:
        return np.array([], dtype=bool)

    mask_trait_absent = np.asarray(mask_trait_absent, dtype=bool)
    mask_trait_present = np.asarray(mask_trait_present, dtype=bool)
    if (mask_trait_absent & mask_trait_present).any():
        raise ValueError("conflicting trait presence/absence masks")

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if not alifestd_is_strictly_bifurcating_asexual(phylogeny_df):
        raise ValueError("phylogeny_df must be strictly bifurcating")

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)
    phylogeny_df["fitch_trait_set"] = (
        mask_trait_absent + 2 * mask_trait_present
    )

    if "node_depth" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_node_depth_asexual(
            phylogeny_df, mutate=True
        )
    max_depth = phylogeny_df["node_depth"].max()

    if alifestd_has_contiguous_ids(phylogeny_df):
        ancestor_iloc = phylogeny_df["ancestor_id"].values
    else:
        phylogeny_df.set_index("id", drop=False, inplace=True)
        ancestor_iloc = phylogeny_df.index.get_indexer(
            phylogeny_df["ancestor_id"].values,
        )

    phylogeny_df["fitch_trait_intersect"] = 0

    ft_intersect = phylogeny_df["fitch_trait_intersect"].to_numpy(copy=False)
    ft_set = phylogeny_df["fitch_trait_set"].to_numpy(copy=False)
    ft_union = ft_set.copy()
    node_depth = phylogeny_df["node_depth"].to_numpy(copy=False)

    # bottom-up pass
    for __ in progress_wrap(range(max_depth + 1), desc="bottom-up pass"):
        ft_intersect[:] = 3
        # at each parent, calculate intersection of children's trait sets
        np.bitwise_and.at(
            ft_intersect,
            ancestor_iloc,
            np.where(node_depth == 0, 3, ft_set),  # handle roof self-loop
        )

        # at each parent, calculate union of children's trait sets
        np.bitwise_or.at(ft_union, ancestor_iloc, ft_set)

        # trait set is intersection if nonempty, else union
        # only update trait set if not already set
        ft_set = np.where(
            ft_set == 0,
            np.where(ft_intersect == 0, ft_union, ft_intersect),
            ft_set,
        )

    # top-down pass
    default_root = 1  # root assumed to be trait absent
    ambiguous_root_mask = (node_depth == 0) & (ft_set == 3)
    ft_set[ambiguous_root_mask] = default_root
    for depth in progress_wrap(range(1, max_depth + 1), desc="top-down pass"):
        layer_mask = node_depth == depth
        traitless_mask = ft_set == 0
        common_trait = ft_set & ft_set[ancestor_iloc]
        # inherit shared trait
        inherit_mask = layer_mask & (
            common_trait.astype(bool) | traitless_mask
        )
        ft_set[inherit_mask] = common_trait[inherit_mask]
        assert (np.bitwise_count(ft_set[layer_mask]) == 1).all()

    # finalization
    ft_set >>= 1  # map {1, 2} to {False, True}
    phylogeny_df["alifestd_screen_trait_defined_clades_fitch_asexual"] = (
        # root self-loop ok: mutation at root not considered a change
        (~ft_set[ancestor_iloc])
        & ft_set
    ).astype(bool)
    phylogeny_df.drop(
        columns=["fitch_trait_set", "fitch_trait_intersect"],
        inplace=True,
    )
    return phylogeny_df[
        "alifestd_screen_trait_defined_clades_fitch_asexual"
    ].values
