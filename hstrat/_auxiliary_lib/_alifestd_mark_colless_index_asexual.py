import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_mark_num_leaves_asexual import alifestd_mark_num_leaves_asexual
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_mark_colless_index_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `colless_index` with Colless imbalance index for each subtree.

    The Colless index is a measure of tree imbalance. For each internal node,
    it computes the sum of pairwise absolute differences in leaf counts among
    children. The value at each node represents the total Colless index for the
    subtree rooted at that node.

    For strictly bifurcating trees, this is sum over internal nodes of |L - R|
    where L and R are leaf counts in left and right subtrees. For polytomies,
    this is generalized to sum over all pairs of children |n_i - n_j|.

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
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if len(phylogeny_df) == 0:
        phylogeny_df["colless_index"] = pd.Series(dtype=int)
        return phylogeny_df

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    if "num_leaves" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_num_leaves_asexual(
            phylogeny_df, mutate=True
        )

    # Use contiguous indexing for efficient array operations
    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
        use_contiguous = True
    else:
        phylogeny_df.index = phylogeny_df["id"]
        use_contiguous = False

    n = len(phylogeny_df)
    colless_index = np.zeros(n, dtype=np.int64)

    if use_contiguous:
        ancestor_ids = phylogeny_df["ancestor_id"].values
        num_leaves = phylogeny_df["num_leaves"].values

        # Step 1: Compute local Colless contribution for each internal node
        # Group children by ancestor and compute pairwise leaf count differences
        # First, collect children's leaf counts for each parent
        children_leaves = [[] for _ in range(n)]
        for idx in range(n):
            ancestor_id = ancestor_ids[idx]
            if ancestor_id != idx:  # Not a root
                children_leaves[ancestor_id].append(num_leaves[idx])

        # Compute local Colless for each node (sum of pairwise |n_i - n_j|)
        local_colless = np.zeros(n, dtype=np.int64)
        for idx in range(n):
            child_counts = children_leaves[idx]
            if len(child_counts) >= 2:
                # Sum of all pairwise absolute differences
                for i in range(len(child_counts)):
                    for j in range(i + 1, len(child_counts)):
                        local_colless[idx] += abs(
                            child_counts[i] - child_counts[j]
                        )

        # Step 2: Accumulate subtree Colless (bottom-up)
        # colless_index[node] = local_colless[node] + sum of children's colless
        for idx_r in range(n):
            idx = n - 1 - idx_r  # Reverse order (leaves to root)
            ancestor_id = ancestor_ids[idx]
            colless_index[idx] += local_colless[idx]
            if ancestor_id != idx:  # Not a root
                colless_index[ancestor_id] += colless_index[idx]

        phylogeny_df["colless_index"] = colless_index
    else:
        # Slow path for non-contiguous IDs
        ids = phylogeny_df["id"].values
        ancestor_ids = phylogeny_df["ancestor_id"].values
        num_leaves_col = phylogeny_df["num_leaves"]

        # Build children mapping
        children_leaves = {id_: [] for id_ in ids}
        for idx, row in phylogeny_df.iterrows():
            node_id = row["id"]
            ancestor_id = row["ancestor_id"]
            if ancestor_id != node_id:  # Not a root
                children_leaves[ancestor_id].append(row["num_leaves"])

        # Compute local Colless for each node
        local_colless = {}
        for node_id in ids:
            child_counts = children_leaves[node_id]
            local_val = 0
            if len(child_counts) >= 2:
                for i in range(len(child_counts)):
                    for j in range(i + 1, len(child_counts)):
                        local_val += abs(child_counts[i] - child_counts[j])
            local_colless[node_id] = local_val

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
