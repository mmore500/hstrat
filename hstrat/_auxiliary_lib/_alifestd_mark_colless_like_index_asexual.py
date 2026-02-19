import math

import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import (
    alifestd_is_topologically_sorted,
)
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import (
    alifestd_try_add_ancestor_id_col,
)
from ._jit import jit

_LN_E = 1.0  # ln(e) = 1.0, used as f(0)


@jit(nopython=True)
def alifestd_mark_colless_like_index_asexual_fast_path(
    ancestor_ids: np.ndarray,
) -> np.ndarray:
    """Implementation detail for
    `alifestd_mark_colless_like_index_asexual`.
    """
    n = len(ancestor_ids)

    # Compute out-degree (number of children) for each node
    num_children = np.zeros(n, dtype=np.int64)
    for idx in range(n):
        if ancestor_ids[idx] != idx:  # Not a root
            num_children[ancestor_ids[idx]] += 1

    # Compute f-size bottom-up
    # f(k) = ln(k + e), so f(0) = ln(e) = 1.0
    # δ_f(T_v) = f(deg(v)) + sum of δ_f(T_c) for children c
    f_size = np.zeros(n, dtype=np.float64)
    for idx in range(n):
        f_size[idx] = math.log(num_children[idx] + math.e)

    # Accumulate f-size bottom-up (add children's f-sizes to parent)
    for idx_r in range(n):
        idx = n - 1 - idx_r
        ancestor_id = ancestor_ids[idx]
        if ancestor_id != idx:
            f_size[ancestor_id] += f_size[idx]

    # Build CSR-like structure of children f-sizes per parent
    offsets = np.zeros(n + 1, dtype=np.int64)
    for i in range(n):
        offsets[i + 1] = offsets[i] + num_children[i]

    total_children = offsets[n]
    children_fsize = np.zeros(total_children, dtype=np.float64)
    fill_pos = np.zeros(n, dtype=np.int64)
    for idx in range(n):
        ancestor_id = ancestor_ids[idx]
        if ancestor_id != idx:
            pos = offsets[ancestor_id] + fill_pos[ancestor_id]
            children_fsize[pos] = f_size[idx]
            fill_pos[ancestor_id] += 1

    # Compute local balance: MDM of children f-sizes
    local_balance = np.zeros(n, dtype=np.float64)
    for idx in range(n):
        k = num_children[idx]
        if k < 2:
            continue
        start = offsets[idx]
        end = offsets[idx + 1]

        # Sort children f-sizes for median computation
        vals = children_fsize[start:end].copy()
        vals.sort()

        # Compute median
        if k % 2 == 1:
            median = vals[k // 2]
        else:
            median = (vals[k // 2 - 1] + vals[k // 2]) / 2.0

        # MDM = (1/k) * sum |x_i - median|
        total = 0.0
        for i in range(k):
            total += abs(vals[i] - median)
        local_balance[idx] = total / k

    # Accumulate subtree Colless-like index bottom-up
    colless_like = np.zeros(n, dtype=np.float64)
    for idx_r in range(n):
        idx = n - 1 - idx_r
        colless_like[idx] += local_balance[idx]
        ancestor_id = ancestor_ids[idx]
        if ancestor_id != idx:
            colless_like[ancestor_id] += colless_like[idx]

    return colless_like


def alifestd_mark_colless_like_index_asexual_slow_path(
    phylogeny_df: pd.DataFrame,
) -> np.ndarray:
    """Implementation detail for
    `alifestd_mark_colless_like_index_asexual`.
    """
    phylogeny_df.index = phylogeny_df["id"]
    ids = phylogeny_df["id"].values

    def f(k):
        return math.log(k + math.e)

    # Build children mapping and compute out-degrees
    children_of = {id_: [] for id_ in ids}
    for idx, row in phylogeny_df.iterrows():
        node_id = row["id"]
        ancestor_id = row["ancestor_id"]
        if ancestor_id != node_id:
            children_of[ancestor_id].append(node_id)

    num_children = {id_: len(children_of[id_]) for id_ in ids}

    # Compute f-size bottom-up
    f_size = {}
    for idx in reversed(phylogeny_df.index):
        node_id = phylogeny_df.at[idx, "id"]
        f_size[node_id] = f(num_children[node_id]) + sum(
            f_size[c] for c in children_of[node_id]
        )

    # Compute local balance (MDM of children f-sizes)
    local_balance = {}
    for node_id in ids:
        k = num_children[node_id]
        if k < 2:
            local_balance[node_id] = 0.0
            continue
        vals = sorted(f_size[c] for c in children_of[node_id])
        if k % 2 == 1:
            median = vals[k // 2]
        else:
            median = (vals[k // 2 - 1] + vals[k // 2]) / 2.0
        total = sum(abs(v - median) for v in vals)
        local_balance[node_id] = total / k

    # Accumulate bottom-up
    colless_dict = {id_: local_balance[id_] for id_ in ids}
    for idx in reversed(phylogeny_df.index):
        node_id = phylogeny_df.at[idx, "id"]
        ancestor_id = phylogeny_df.at[idx, "ancestor_id"]
        if ancestor_id != node_id:
            colless_dict[ancestor_id] += colless_dict[node_id]

    return phylogeny_df["id"].map(colless_dict).values


def alifestd_mark_colless_like_index_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `colless_like_index` with Colless-like index for
    each subtree.

    Computes the Colless-like balance index from Mir, Rossello, and
    Rotger (2018) that supports polytomies. Uses weight function
    f(k) = ln(k + e) and the mean deviation from the median (MDM)
    as dissimilarity.

    For each internal node v with children v_1, ..., v_k:
        bal(v) = MDM(delta_f(T_v1), ..., delta_f(T_vk))

    where delta_f(T) is the f-size of subtree T, defined as the sum
    of f(deg(u)) over all nodes u in T, and MDM is the mean deviation
    from the median.

    The Colless-like index at a node is the sum of balance values
    across all internal nodes in its subtree.

    For strictly bifurcating trees, consider using
    `alifestd_mark_colless_index_asexual` for the classic Colless
    index.

    Leaf nodes will have Colless-like index 0. The root node contains
    the Colless-like index for the entire tree.

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
        Phylogeny DataFrame with an additional column
        "colless_like_index" containing the Colless-like imbalance
        index for the subtree rooted at each node.

    References
    ----------
    Mir, A., Rossello, F., & Rotger, L. (2018). Sound Colless-like
    balance indices for multifurcating trees. PLOS ONE, 13(9),
    e0203401. https://doi.org/10.1371/journal.pone.0203401

    See Also
    --------
    alifestd_mark_colless_index_asexual :
        Classic Colless index for strictly bifurcating trees.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if len(phylogeny_df) == 0:
        phylogeny_df["colless_like_index"] = pd.Series(dtype=float)
        return phylogeny_df

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
        phylogeny_df[
            "colless_like_index"
        ] = alifestd_mark_colless_like_index_asexual_fast_path(
            phylogeny_df["ancestor_id"].to_numpy(),
        )
    elif not alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df[
            "colless_like_index"
        ] = alifestd_mark_colless_like_index_asexual_slow_path(
            phylogeny_df,
        )
    else:
        assert False

    return phylogeny_df
