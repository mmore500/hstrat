import math

import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import (
    alifestd_is_topologically_sorted,
)
from ._alifestd_mark_num_children_asexual import (
    alifestd_mark_num_children_asexual,
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
    for idx in range(n):
        ancestor_id = ancestor_ids[idx]
        if ancestor_id != idx:  # Not a root
            num_children[ancestor_id] += 1

    # Compute f-size bottom-up
    # f(k) = ln(k + e), so f(0) = ln(e) = 1.0
    # delta_f(T_v) = f(deg(v)) + sum of delta_f(T_c) for children c
    f_size = np.zeros(n, dtype=np.float64)
    for idx in range(n):
        f_size[idx] = math.log(num_children[idx] + math.e)

    # Accumulate f-size bottom-up (add children's f-sizes to parent)
    for i in range(n - 1, -1, -1):
        ancestor_id = ancestor_ids[i]
        if ancestor_id != i:  # Not a root
            f_size[ancestor_id] += f_size[i]

    # Build CSR-like structure of children f-sizes per parent
    offsets = np.zeros(n + 1, dtype=np.int64)
    for i, k in enumerate(num_children):
        offsets[i + 1] = offsets[i] + k

    total_children = offsets[n]
    children_fsize = np.zeros(total_children, dtype=np.float64)
    fill_pos = np.zeros(n, dtype=np.int64)
    for idx, ancestor_id in enumerate(ancestor_ids):
        if ancestor_id != idx:  # Not a root
            pos = offsets[ancestor_id] + fill_pos[ancestor_id]
            children_fsize[pos] = f_size[idx]
            fill_pos[ancestor_id] += 1

    # Compute local balance using selected dissimilarity
    local_balance = np.zeros(n, dtype=np.float64)
    for idx, k in enumerate(num_children):
        if k >= 2:
            start = offsets[idx]
            end = offsets[idx + 1]

            vals = children_fsize[start:end]

            if diss_type == 0:  # MDM
                median = np.median(vals)
                # MDM = (1/k) * sum |x_i - median|
                local_balance[idx] = np.sum(np.abs(vals - median)) / k

            elif diss_type == 1:  # Variance (ddof=1)
                # np.var uses ddof=0; apply Bessel correction
                local_balance[idx] = np.var(vals) * k / (k - 1)

            elif diss_type == 2:  # Standard deviation (ddof=1)
                local_balance[idx] = math.sqrt(np.var(vals) * k / (k - 1))

    # Accumulate subtree Colless-like index bottom-up
    colless_like = np.zeros(n, dtype=np.float64)
    for i in range(n - 1, -1, -1):
        ancestor_id = ancestor_ids[i]
        colless_like[i] += local_balance[i]
        if ancestor_id != i:  # Not a root
            colless_like[ancestor_id] += colless_like[i]

    return colless_like


def _colless_like_slow_path(
    phylogeny_df: pd.DataFrame,
    diss_type: str,
) -> np.ndarray:
    """Implementation detail for Colless-like index functions."""
    phylogeny_df.index = phylogeny_df["id"]

    # Build children mapping
    children_of = {id_: [] for id_ in phylogeny_df.index}
    for node_id in phylogeny_df.index:
        ancestor_id = phylogeny_df.at[node_id, "ancestor_id"]
        if ancestor_id != node_id:  # Not a root
            children_of[ancestor_id].append(node_id)

    # Compute f-size bottom-up
    f_size = {}
    for node_id in reversed(phylogeny_df.index):
        k = phylogeny_df.at[node_id, "num_children"]
        f_size[node_id] = math.log(k + math.e) + sum(
            f_size[c] for c in children_of[node_id]
        )

    # Compute local balance using selected dissimilarity
    local_balance = {}
    for node_id in phylogeny_df.index:
        k = phylogeny_df.at[node_id, "num_children"]
        if k >= 2:
            vals = np.array(
                [f_size[c] for c in children_of[node_id]],
            )

            if diss_type == "mdm":
                med = np.median(vals)
                local_balance[node_id] = np.sum(np.abs(vals - med)) / k
            elif diss_type == "var":
                local_balance[node_id] = np.var(vals, ddof=1)
            elif diss_type == "sd":
                local_balance[node_id] = np.std(vals, ddof=1)
            else:
                assert False
        else:
            local_balance[node_id] = 0.0

    # Accumulate bottom-up
    for node_id in reversed(phylogeny_df.index):
        ancestor_id = phylogeny_df.at[node_id, "ancestor_id"]
        if ancestor_id != node_id:  # Not a root
            local_balance[ancestor_id] += local_balance[node_id]

    return phylogeny_df["id"].map(local_balance).values


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
        phylogeny_df[col_name] = _colless_like_fast_path(
            phylogeny_df["ancestor_id"].to_numpy(),
            ["mdm", "var", "sd"].index(diss_type),
        )
    else:
        if "num_children" not in phylogeny_df.columns:
            phylogeny_df = alifestd_mark_num_children_asexual(
                phylogeny_df,
                mutate=True,
            )
        phylogeny_df[col_name] = _colless_like_slow_path(
            phylogeny_df,
            diss_type,
        )

    return phylogeny_df
