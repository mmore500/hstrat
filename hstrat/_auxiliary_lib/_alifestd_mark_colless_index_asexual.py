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
from ._jit import jit


@jit(nopython=True)
def alifestd_mark_colless_index_asexual_fast_path(
    ancestor_ids: np.ndarray,
    num_leaves: np.ndarray,
) -> np.ndarray:
    """Implementation detail for `alifestd_mark_colless_index_asexual`."""
    n = len(ancestor_ids)

    # For strictly bifurcating trees, track first child's leaf count
    # Use -1 as sentinel for "no child seen yet"
    first_child_leaves = np.full(n, -1, dtype=np.int64)
    local_colless = np.zeros(n, dtype=np.int64)

    # Forward pass: record children leaf counts, compute local colless
    for idx in range(n):
        ancestor_id = ancestor_ids[idx]
        if ancestor_id != idx:  # Not a root
            if first_child_leaves[ancestor_id] == -1:
                # First child seen
                first_child_leaves[ancestor_id] = num_leaves[idx]
            else:
                # Second child - compute local colless as |L - R|
                local_colless[ancestor_id] = abs(
                    first_child_leaves[ancestor_id] - num_leaves[idx]
                )

    # Reverse pass: accumulate subtree colless bottom-up
    colless_index = np.zeros(n, dtype=np.int64)
    for idx_r in range(n):
        idx = n - 1 - idx_r  # Reverse order (leaves to root)
        colless_index[idx] += local_colless[idx]
        ancestor_id = ancestor_ids[idx]
        if ancestor_id != idx:  # Not a root
            colless_index[ancestor_id] += colless_index[idx]

    return colless_index


def alifestd_mark_colless_index_asexual_slow_path(
    phylogeny_df: pd.DataFrame,
) -> pd.DataFrame:
    """Implementation detail for `alifestd_mark_colless_index_asexual`."""
    phylogeny_df.index = phylogeny_df["id"]
    ids = phylogeny_df["id"].values

    # Build children mapping
    children_leaves = {id_: [] for id_ in ids}
    for idx, row in phylogeny_df.iterrows():
        node_id = row["id"]
        ancestor_id = row["ancestor_id"]
        if ancestor_id != node_id:  # Not a root
            children_leaves[ancestor_id].append(row["num_leaves"])

    # Compute local Colless for each node
    local_colless = {}
    for node_id, child_counts in children_leaves.items():
        if len(child_counts) == 2:
            local_colless[node_id] = abs(child_counts[0] - child_counts[1])
        else:
            local_colless[node_id] = 0

    # Initialize colless_index with local values
    colless_dict = {node_id: local_colless[node_id] for node_id in ids}

    # Accumulate subtree Colless (bottom-up via reversed iteration)
    for idx in reversed(phylogeny_df.index):
        node_id = phylogeny_df.at[idx, "id"]
        ancestor_id = phylogeny_df.at[idx, "ancestor_id"]
        if ancestor_id != node_id:  # Not a root
            colless_dict[ancestor_id] += colless_dict[node_id]

    phylogeny_df["colless_index"] = phylogeny_df["id"].map(colless_dict)
    return phylogeny_df


def alifestd_mark_colless_index_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `colless_index` with Colless imbalance index for each subtree.

    Computes the classic Colless index for strictly bifurcating trees. For each
    internal node with exactly two children, the local contribution is |L - R|
    where L and R are leaf counts in left and right subtrees. The value at each
    node represents the total Colless index for the subtree rooted at that node.

    Raises ValueError if the tree is not strictly bifurcating. For trees with
    polytomies, use `alifestd_mark_colless_index_generalized_asexual` instead.

    Leaf nodes will have Colless index 0 (no imbalance in subtree of size 1).
    The root node contains the Colless index for the entire tree.

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
        Phylogeny DataFrame with an additional column "colless_index"
        containing the Colless imbalance index for the subtree rooted at each
        node.

    Raises
    ------
    ValueError
        If phylogeny_df is not strictly bifurcating.

    See Also
    --------
    alifestd_mark_colless_index_generalized_asexual :
        Generalized Colless index that supports polytomies.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if len(phylogeny_df) == 0:
        phylogeny_df["colless_index"] = pd.Series(dtype=int)
        return phylogeny_df

    if not alifestd_is_strictly_bifurcating_asexual(phylogeny_df):
        raise ValueError(
            "phylogeny_df must be strictly bifurcating; "
            "consider using alifestd_mark_colless_index_generalized_asexual "
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
            "colless_index"
        ] = alifestd_mark_colless_index_asexual_fast_path(
            phylogeny_df["ancestor_id"].to_numpy(),
            phylogeny_df["num_leaves"].to_numpy(),
        )
        return phylogeny_df
    else:
        return alifestd_mark_colless_index_asexual_slow_path(phylogeny_df)
