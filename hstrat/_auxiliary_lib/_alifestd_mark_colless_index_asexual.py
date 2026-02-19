import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_strictly_bifurcating_asexual import (
    alifestd_is_strictly_bifurcating_asexual,
)
from ._alifestd_is_topologically_sorted import (
    alifestd_is_topologically_sorted,
)
from ._alifestd_mark_left_child_asexual import (
    alifestd_mark_left_child_asexual,
)
from ._alifestd_mark_num_leaves_asexual import (
    alifestd_mark_num_leaves_asexual,
)
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import (
    alifestd_try_add_ancestor_id_col,
)
from ._jit import jit
from ._reversed_enumerate import reversed_enumerate_jit


@jit(nopython=True)
def alifestd_mark_colless_index_asexual_fast_path(
    ancestor_ids: np.ndarray,
    num_leaves: np.ndarray,
    left_child_ids: np.ndarray,
) -> np.ndarray:
    """Implementation detail for
    `alifestd_mark_colless_index_asexual`.
    """
    n = len(ancestor_ids)

    # Compute local colless for each internal node
    # For bifurcating: right_leaves = num_leaves[node] - num_leaves[left]
    local_colless = np.zeros(n, dtype=np.int64)
    for idx, left_child in enumerate(left_child_ids):
        if left_child != idx:  # Has children (internal node)
            left_leaves = num_leaves[left_child]
            right_leaves = num_leaves[idx] - left_leaves
            local_colless[idx] = abs(left_leaves - right_leaves)

    # Reverse pass: accumulate subtree colless bottom-up
    colless_index = np.zeros(n, dtype=np.int64)
    for idx, ancestor_id in reversed_enumerate_jit(ancestor_ids):
        colless_index[idx] += local_colless[idx]
        if ancestor_id != idx:  # Not a root
            colless_index[ancestor_id] += colless_index[idx]

    return colless_index


def alifestd_mark_colless_index_asexual_slow_path(
    phylogeny_df: pd.DataFrame,
) -> np.ndarray:
    """Implementation detail for
    `alifestd_mark_colless_index_asexual`.
    """
    phylogeny_df.index = phylogeny_df["id"]

    # Compute local colless using left_child approach
    local_colless = {}
    for node_id in phylogeny_df.index:
        left_child = phylogeny_df.at[node_id, "left_child_id"]
        if left_child != node_id:  # Has children (internal node)
            left_leaves = phylogeny_df.at[left_child, "num_leaves"]
            right_leaves = phylogeny_df.at[node_id, "num_leaves"] - left_leaves
            local_colless[node_id] = abs(left_leaves - right_leaves)
        else:
            local_colless[node_id] = 0

    # Accumulate subtree Colless (bottom-up via reversed iteration)
    for node_id in reversed(phylogeny_df.index):
        ancestor_id = phylogeny_df.at[node_id, "ancestor_id"]
        if ancestor_id != node_id:  # Not a root
            local_colless[ancestor_id] += local_colless[node_id]

    return phylogeny_df["id"].map(local_colless).values


def alifestd_mark_colless_index_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `colless_index` with Colless imbalance index for
    each subtree.

    Computes the classic Colless index for strictly bifurcating trees.
    For each internal node with exactly two children, the local
    contribution is |L - R| where L and R are leaf counts in left and
    right subtrees. The value at each node represents the total Colless
    index for the subtree rooted at that node.

    Raises ValueError if the tree is not strictly bifurcating. For
    trees with polytomies, use
    `alifestd_mark_colless_like_index_mdm_asexual` for the Colless-like
    index instead.

    Leaf nodes will have Colless index 0 (no imbalance in subtree of
    size 1). The root node contains the Colless index for the entire
    tree.

    A topological sort will be applied if `phylogeny_df` is not
    topologically sorted. Dataframe reindexing (e.g., df.index) may
    be applied.

    Input dataframe is not mutated by this operation unless `mutate`
    set True. If mutate set True, operation does not occur in place;
    still use return value to get transformed phylogeny dataframe.

    Parameters
    ----------
    phylogeny_df : pd.DataFrame
        Alife standard DataFrame containing the phylogenetic
        relationships.

    mutate : bool, optional
        If True, modify the input DataFrame in place. Default is
        False.

    Returns
    -------
    pd.DataFrame
        Phylogeny DataFrame with an additional column "colless_index"
        containing the Colless imbalance index for the subtree rooted
        at each node.

    Raises
    ------
    ValueError
        If phylogeny_df is not strictly bifurcating.

    See Also
    --------
    alifestd_mark_colless_index_corrected_asexual :
        Normalized Colless index (corrected for tree size).
    alifestd_mark_colless_like_index_mdm_asexual :
        Colless-like index (MDM) that supports polytomies.
    alifestd_mark_colless_like_index_var_asexual :
        Colless-like index (variance) that supports polytomies.
    alifestd_mark_colless_like_index_sd_asexual :
        Colless-like index (std dev) that supports polytomies.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if phylogeny_df.empty:
        phylogeny_df["colless_index"] = pd.Series(dtype=int)
        return phylogeny_df

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)
    if "ancestor_id" not in phylogeny_df.columns:
        raise ValueError(
            "alifestd_mark_colless_index_asexual only supports "
            "asexual phylogenies.",
        )

    if not alifestd_is_strictly_bifurcating_asexual(phylogeny_df):
        raise ValueError(
            "phylogeny_df must be strictly bifurcating; "
            "consider using "
            "alifestd_mark_colless_like_index_mdm_asexual "
            "for the Colless-like index for trees with polytomies",
        )

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    if "num_leaves" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_num_leaves_asexual(
            phylogeny_df, mutate=True
        )

    if "left_child_id" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_left_child_asexual(
            phylogeny_df, mutate=True
        )

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df[
            "colless_index"
        ] = alifestd_mark_colless_index_asexual_fast_path(
            phylogeny_df["ancestor_id"].to_numpy(),
            phylogeny_df["num_leaves"].to_numpy(),
            phylogeny_df["left_child_id"].to_numpy(),
        )
    else:
        phylogeny_df[
            "colless_index"
        ] = alifestd_mark_colless_index_asexual_slow_path(
            phylogeny_df,
        )

    return phylogeny_df
