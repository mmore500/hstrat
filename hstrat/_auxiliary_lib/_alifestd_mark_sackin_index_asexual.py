import typing

import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_strictly_bifurcating_asexual import (
    alifestd_is_strictly_bifurcating_asexual,
)
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_mark_num_leaves_asexual import alifestd_mark_num_leaves_asexual
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_mark_sackin_index_asexual_fast_path(
    ancestor_ids: np.ndarray,
    num_leaves: np.ndarray,
) -> np.ndarray:
    """Implementation detail for `alifestd_mark_sackin_index_asexual`."""
    n = len(ancestor_ids)
    sackin_index = np.zeros(n, dtype=np.int64)

    # Count children for each node to identify bifurcating nodes
    num_children: typing.List[int] = [0] * n
    for idx, ancestor_id in enumerate(ancestor_ids):
        if ancestor_id != idx:  # Not a root
            num_children[ancestor_id] += 1

    # Accumulate Sackin index (bottom-up)
    # sackin[node] = sum over children c of (sackin[c] + num_leaves[c])
    # But only for bifurcating nodes (exactly 2 children)
    for idx_r, ancestor_id in enumerate(ancestor_ids[::-1]):
        idx = n - 1 - idx_r  # Reverse order (leaves to root)
        if ancestor_id != idx:  # Not a root
            # Only accumulate if parent is bifurcating
            if num_children[ancestor_id] == 2:
                sackin_index[ancestor_id] += (
                    sackin_index[idx] + num_leaves[idx]
                )

    return sackin_index


def alifestd_mark_sackin_index_asexual_slow_path(
    phylogeny_df: pd.DataFrame,
) -> pd.DataFrame:
    """Implementation detail for `alifestd_mark_sackin_index_asexual`."""
    phylogeny_df.index = phylogeny_df["id"]
    ids = phylogeny_df["id"].values

    # Count children for each node
    num_children: typing.Dict[int, int] = {id_: 0 for id_ in ids}
    for idx, row in phylogeny_df.iterrows():
        node_id = row["id"]
        ancestor_id = row["ancestor_id"]
        if ancestor_id != node_id:  # Not a root
            num_children[ancestor_id] += 1

    # Initialize Sackin index
    sackin_dict: typing.Dict[int, int] = {id_: 0 for id_ in ids}

    # Accumulate Sackin index (bottom-up)
    for idx in reversed(phylogeny_df.index):
        node_id = phylogeny_df.at[idx, "id"]
        ancestor_id = phylogeny_df.at[idx, "ancestor_id"]
        if ancestor_id != node_id:  # Not a root
            # Only accumulate if parent is bifurcating
            if num_children[ancestor_id] == 2:
                node_leaves = phylogeny_df.at[idx, "num_leaves"]
                sackin_dict[ancestor_id] += sackin_dict[node_id] + node_leaves

    phylogeny_df["sackin_index"] = phylogeny_df["id"].map(sackin_dict)
    return phylogeny_df


def alifestd_mark_sackin_index_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `sackin_index` with Sackin imbalance index for each subtree.

    Computes the Sackin index for strictly bifurcating trees. The Sackin index
    is the sum of the depths of all leaves in the subtree. For each internal
    node with exactly two children, the contribution is the sum of leaf depths
    in its subtree.

    Raises ValueError if the tree is not strictly bifurcating. For trees with
    polytomies, use `alifestd_mark_sackin_index_generalized_asexual` instead.

    Leaf nodes will have Sackin index 0. The root node contains the Sackin
    index for the entire tree.

    A topological sort will be applied if `phylogeny_df` is not topologically
    sorted. Dataframe reindexing (e.g., df.index) may be applied.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.

    Parameters
    ----------
    phylogeny_df : pd.DataFrame
        Alife standard DataFrame containing the phylogenetic relationships.

    mutate : bool, optional
        If True, modify the input DataFrame in place. Default is False.

    Returns
    -------
    pd.DataFrame
        Phylogeny DataFrame with an additional column "sackin_index"
        containing the Sackin imbalance index for the subtree rooted at each
        node.

    Raises
    ------
    ValueError
        If phylogeny_df is not strictly bifurcating.

    See Also
    --------
    alifestd_mark_sackin_index_generalized_asexual :
        Generalized Sackin index that supports polytomies.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if len(phylogeny_df) == 0:
        phylogeny_df["sackin_index"] = pd.Series(dtype=int)
        return phylogeny_df

    if not alifestd_is_strictly_bifurcating_asexual(phylogeny_df):
        raise ValueError(
            "phylogeny_df must be strictly bifurcating; "
            "consider using alifestd_mark_sackin_index_generalized_asexual "
            "for trees with polytomies"
        )

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    if "num_leaves" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_num_leaves_asexual(
            phylogeny_df, mutate=True
        )

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
        phylogeny_df[
            "sackin_index"
        ] = alifestd_mark_sackin_index_asexual_fast_path(
            phylogeny_df["ancestor_id"].to_numpy(),
            phylogeny_df["num_leaves"].to_numpy(),
        )
        return phylogeny_df
    else:
        return alifestd_mark_sackin_index_asexual_slow_path(phylogeny_df)
