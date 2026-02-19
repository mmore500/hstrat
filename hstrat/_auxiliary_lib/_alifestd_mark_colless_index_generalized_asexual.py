import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_mark_num_leaves_asexual import alifestd_mark_num_leaves_asexual
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._jit import jit


@jit(nopython=True)
def alifestd_mark_colless_index_generalized_asexual_fast_path(
    ancestor_ids: np.ndarray,
    num_leaves: np.ndarray,
) -> np.ndarray:
    """Implementation detail for
    `alifestd_mark_colless_index_generalized_asexual`.
    """
    n = len(ancestor_ids)

    # Count children per node
    num_children = np.zeros(n, dtype=np.int64)
    for idx in range(n):
        if ancestor_ids[idx] != idx:  # Not a root
            num_children[ancestor_ids[idx]] += 1

    # Build CSR-like offsets
    offsets = np.zeros(n + 1, dtype=np.int64)
    for i in range(n):
        offsets[i + 1] = offsets[i] + num_children[i]

    # Fill flat children_leaves array
    total_children = offsets[n]
    children_leaves = np.zeros(total_children, dtype=np.int64)
    fill_pos = np.zeros(n, dtype=np.int64)
    for idx in range(n):
        ancestor_id = ancestor_ids[idx]
        if ancestor_id != idx:  # Not a root
            pos = offsets[ancestor_id] + fill_pos[ancestor_id]
            children_leaves[pos] = num_leaves[idx]
            fill_pos[ancestor_id] += 1

    # Compute local colless (sum of pairwise |c_i - c_j|)
    local_colless = np.zeros(n, dtype=np.int64)
    for idx in range(n):
        start = offsets[idx]
        end = offsets[idx + 1]
        for i in range(start, end):
            for j in range(i + 1, end):
                local_colless[idx] += abs(children_leaves[i] - children_leaves[j])

    # Accumulate subtree colless bottom-up
    colless_index = np.zeros(n, dtype=np.int64)
    for idx_r in range(n):
        idx = n - 1 - idx_r  # Reverse order (leaves to root)
        colless_index[idx] += local_colless[idx]
        ancestor_id = ancestor_ids[idx]
        if ancestor_id != idx:  # Not a root
            colless_index[ancestor_id] += colless_index[idx]

    return colless_index


def alifestd_mark_colless_index_generalized_asexual_slow_path(
    phylogeny_df: pd.DataFrame,
) -> pd.DataFrame:
    """Implementation detail for
    `alifestd_mark_colless_index_generalized_asexual`.
    """
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
        local_val = 0
        if len(child_counts) >= 2:
            for i, count_i in enumerate(child_counts):
                for count_j in child_counts[i + 1 :]:
                    local_val += abs(count_i - count_j)
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


def alifestd_mark_colless_index_generalized_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `colless_index` with generalized Colless index for each
    subtree.

    Computes a generalized Colless imbalance index that supports polytomies.
    For each internal node, it computes the sum of pairwise absolute differences
    in leaf counts among all children. The value at each node represents the
    total Colless index for the subtree rooted at that node.

    For a node with k children having n_1, n_2, ..., n_k leaves respectively,
    the local contribution is sum_{i<j} |n_i - n_j|.

    For strictly bifurcating trees (k=2), this reduces to the classic Colless
    index |L - R|. For trees known to be strictly bifurcating, consider using
    `alifestd_mark_colless_index_asexual` for slightly better performance.

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
        containing the generalized Colless imbalance index for the subtree
        rooted at each node.

    See Also
    --------
    alifestd_mark_colless_index_asexual :
        Classic Colless index for strictly bifurcating trees.
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

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
        phylogeny_df[
            "colless_index"
        ] = alifestd_mark_colless_index_generalized_asexual_fast_path(
            phylogeny_df["ancestor_id"].to_numpy(),
            phylogeny_df["num_leaves"].to_numpy(),
        )
        return phylogeny_df
    else:
        return alifestd_mark_colless_index_generalized_asexual_slow_path(
            phylogeny_df,
        )
