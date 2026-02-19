import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_mark_num_leaves_asexual import alifestd_mark_num_leaves_asexual
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._jit import jit
from ._reversed_enumerate import reversed_enumerate_jit


@jit(nopython=True)
def alifestd_mark_sackin_index_asexual_fast_path(
    ancestor_ids: np.ndarray,
    num_leaves: np.ndarray,
) -> np.ndarray:
    """Implementation detail for `alifestd_mark_sackin_index_asexual`."""
    n = len(ancestor_ids)
    sackin_index = np.zeros(n, dtype=np.int64)

    # Accumulate Sackin index (bottom-up)
    # sackin[node] = sum over children c of (sackin[c] + num_leaves[c])
    for idx, ancestor_id in reversed_enumerate_jit(ancestor_ids):
        if ancestor_id != idx:  # Not a root
            sackin_index[ancestor_id] += sackin_index[idx] + num_leaves[idx]

    return sackin_index


def alifestd_mark_sackin_index_asexual_slow_path(
    phylogeny_df: pd.DataFrame,
) -> np.ndarray:
    """Implementation detail for `alifestd_mark_sackin_index_asexual`."""
    phylogeny_df.index = phylogeny_df["id"]

    # Initialize Sackin index
    sackin_dict = {id_: 0 for id_ in phylogeny_df.index}

    # Accumulate Sackin index (bottom-up)
    for node_id in reversed(phylogeny_df.index):
        ancestor_id = phylogeny_df.at[node_id, "ancestor_id"]
        if ancestor_id != node_id:  # Not a root
            node_leaves = phylogeny_df.at[node_id, "num_leaves"]
            sackin_dict[ancestor_id] += sackin_dict[node_id] + node_leaves

    return phylogeny_df["id"].map(sackin_dict).values


def alifestd_mark_sackin_index_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `sackin_index` with Sackin index for each subtree.

    Computes the Sackin imbalance index, which is the sum of the depths
    of all leaves in the subtree. For each internal node, the
    contribution is the sum of leaf depths in its subtree.

    For a node with children c_1, c_2, ..., c_k:
        sackin[node] = sum_{i} (sackin[c_i] + num_leaves[c_i])

    This formula naturally supports both bifurcating trees and trees
    with polytomies.

    Leaf nodes will have Sackin index 0. The root node contains the
    Sackin index for the entire tree.

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
        Phylogeny DataFrame with an additional column "sackin_index"
        containing the Sackin imbalance index for the subtree rooted
        at each node.

    See Also
    --------
    alifestd_mark_colless_index_asexual :
        Colless index for strictly bifurcating trees.
    alifestd_mark_colless_like_index_mdm_asexual :
        Colless-like index that supports polytomies.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if len(phylogeny_df) == 0:
        phylogeny_df["sackin_index"] = pd.Series(dtype=int)
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
            "sackin_index"
        ] = alifestd_mark_sackin_index_asexual_fast_path(
            phylogeny_df["ancestor_id"].to_numpy(),
            phylogeny_df["num_leaves"].to_numpy(),
        )
    else:
        phylogeny_df[
            "sackin_index"
        ] = alifestd_mark_sackin_index_asexual_slow_path(
            phylogeny_df,
        )

    return phylogeny_df
