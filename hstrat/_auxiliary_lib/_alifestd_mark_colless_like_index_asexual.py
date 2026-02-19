import math
import statistics

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


@jit(nopython=True)
def _colless_like_fast_path(
    ancestor_ids: np.ndarray,
    diss_type: int,
) -> np.ndarray:
    """Implementation detail for Colless-like index functions.

    Parameters
    ----------
    ancestor_ids : np.ndarray
        Array of ancestor IDs (contiguous, topologically sorted).
    diss_type : int
        Dissimilarity type: 0=MDM, 1=variance, 2=std dev.
    """
    n = len(ancestor_ids)

    # Compute out-degree (number of children) for each node
    num_children = np.zeros(n, dtype=np.int64)
    for idx, ancestor_id in enumerate(ancestor_ids):
        if ancestor_id != idx:  # Not a root
            num_children[ancestor_id] += 1

    # Compute f-size bottom-up
    # f(k) = ln(k + e), so f(0) = ln(e) = 1.0
    # δ_f(T_v) = f(deg(v)) + sum of δ_f(T_c) for children c
    f_size = np.zeros(n, dtype=np.float64)
    for idx, k in enumerate(num_children):
        f_size[idx] = math.log(k + math.e)

    # Accumulate f-size bottom-up (add children's f-sizes to parent)
    for idx in reversed(range(n)):
        ancestor_id = ancestor_ids[idx]
        if ancestor_id != idx:
            f_size[ancestor_id] += f_size[idx]

    # Build CSR-like structure of children f-sizes per parent
    offsets = np.zeros(n + 1, dtype=np.int64)
    for i, k in enumerate(num_children):
        offsets[i + 1] = offsets[i] + k

    total_children = offsets[n]
    children_fsize = np.zeros(total_children, dtype=np.float64)
    fill_pos = np.zeros(n, dtype=np.int64)
    for idx, ancestor_id in enumerate(ancestor_ids):
        if ancestor_id != idx:
            pos = offsets[ancestor_id] + fill_pos[ancestor_id]
            children_fsize[pos] = f_size[idx]
            fill_pos[ancestor_id] += 1

    # Compute local balance using selected dissimilarity
    local_balance = np.zeros(n, dtype=np.float64)
    for idx, k in enumerate(num_children):
        if k < 2:
            continue
        start = offsets[idx]
        end = offsets[idx + 1]

        vals = children_fsize[start:end].copy()
        vals.sort()

        if diss_type == 0:  # MDM
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

        elif diss_type == 1:  # Variance
            # var = (1/(k-1)) * sum (x_i - mean)^2
            mean = 0.0
            for i in range(k):
                mean += vals[i]
            mean /= k

            total = 0.0
            for i in range(k):
                diff = vals[i] - mean
                total += diff * diff
            local_balance[idx] = total / (k - 1)

        elif diss_type == 2:  # Standard deviation
            # sd = sqrt(var)
            mean = 0.0
            for i in range(k):
                mean += vals[i]
            mean /= k

            total = 0.0
            for i in range(k):
                diff = vals[i] - mean
                total += diff * diff
            local_balance[idx] = math.sqrt(total / (k - 1))

    # Accumulate subtree Colless-like index bottom-up
    colless_like = np.zeros(n, dtype=np.float64)
    for idx in reversed(range(n)):
        colless_like[idx] += local_balance[idx]
        ancestor_id = ancestor_ids[idx]
        if ancestor_id != idx:
            colless_like[ancestor_id] += colless_like[idx]

    return colless_like


def _colless_like_slow_path(
    phylogeny_df: pd.DataFrame,
    diss_type: str,
) -> np.ndarray:
    """Implementation detail for Colless-like index functions."""
    phylogeny_df.index = phylogeny_df["id"]
    ids = phylogeny_df["id"].values

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
        f_size[node_id] = math.log(num_children[node_id] + math.e) + sum(
            f_size[c] for c in children_of[node_id]
        )

    # Compute local balance using selected dissimilarity
    local_balance = {}
    for node_id in ids:
        k = num_children[node_id]
        if k < 2:
            local_balance[node_id] = 0.0
            continue

        vals = [f_size[c] for c in children_of[node_id]]

        if diss_type == "mdm":
            med = statistics.median(vals)
            local_balance[node_id] = sum(abs(v - med) for v in vals) / k
        elif diss_type == "var":
            local_balance[node_id] = statistics.variance(vals)
        elif diss_type == "sd":
            local_balance[node_id] = statistics.stdev(vals)
        else:
            assert False

    # Accumulate bottom-up
    colless_dict = {id_: local_balance[id_] for id_ in ids}
    for idx in reversed(phylogeny_df.index):
        node_id = phylogeny_df.at[idx, "id"]
        ancestor_id = phylogeny_df.at[idx, "ancestor_id"]
        if ancestor_id != node_id:
            colless_dict[ancestor_id] += colless_dict[node_id]

    return phylogeny_df["id"].map(colless_dict).values


# Mapping from string dissimilarity names to numba-compatible int codes
_DISS_STR_TO_INT = {"mdm": 0, "var": 1, "sd": 2}


def _alifestd_mark_colless_like_index_asexual_impl(
    phylogeny_df: pd.DataFrame,
    col_name: str,
    diss_type: str,
    mutate: bool = False,
) -> pd.DataFrame:
    """Common implementation for Colless-like index variants.

    Parameters
    ----------
    phylogeny_df : pd.DataFrame
        Alife standard DataFrame.
    col_name : str
        Name of the output column.
    diss_type : str
        Dissimilarity type: "mdm", "var", or "sd".
    mutate : bool, optional
        If True, modify the input DataFrame in place.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if phylogeny_df.empty:
        phylogeny_df[col_name] = pd.Series(dtype=float)
        return phylogeny_df

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
        phylogeny_df[col_name] = _colless_like_fast_path(
            phylogeny_df["ancestor_id"].to_numpy(),
            _DISS_STR_TO_INT[diss_type],
        )
    else:
        phylogeny_df[col_name] = _colless_like_slow_path(
            phylogeny_df,
            diss_type,
        )

    return phylogeny_df
