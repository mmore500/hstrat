import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_strictly_bifurcating_asexual import (
    alifestd_is_strictly_bifurcating_asexual,
)
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_mark_is_right_child_asexual import (
    alifestd_mark_is_right_child_asexual,
)
from ._alifestd_mark_num_leaves_asexual import alifestd_mark_num_leaves_asexual
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._jit import jit


@jit(nopython=True)
def _alifestd_mark_num_preceding_leaves_asexual_fast_path(
    ancestor_ids: np.ndarray,
    num_leaves: np.ndarray,
    is_right_child: np.ndarray,
) -> np.ndarray:
    """Implementation detail for
    `alifestd_mark_num_preceding_leaves_asexual`."""

    num_preceding_leaves = np.zeros_like(ancestor_ids)
    for idx, ancestor_id in enumerate(ancestor_ids):
        num_preceding_leaves[idx] = (
            num_preceding_leaves[ancestor_id]
            + (num_leaves[ancestor_id] - num_leaves[idx]) * is_right_child[idx]
        )

    return num_preceding_leaves


def _alifestd_mark_num_preceding_leaves_asexual_slow_path(
    phylogeny_df: pd.DataFrame,
) -> pd.DataFrame:
    """Implementation detail for
    `alifestd_mark_num_preceding_leaves_asexual`."""

    phylogeny_df.index = phylogeny_df["id"]

    phylogeny_df["num_preceding_leaves"] = 0

    for idx in phylogeny_df.index:
        ancestor_id = phylogeny_df.at[idx, "ancestor_id"]
        phylogeny_df.at[idx, "num_preceding_leaves"] = (
            phylogeny_df.at[ancestor_id, "num_preceding_leaves"]
            + (
                phylogeny_df.at[ancestor_id, "num_leaves"]
                - phylogeny_df.at[idx, "num_leaves"]
            )
            * phylogeny_df.at[idx, "is_right_child"]
        )

    return phylogeny_df


def alifestd_mark_num_preceding_leaves_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `num_preceding_leaves` with count of all leaves occuring
    before the present node in an inorder traversal.

    For internal nodes, the number of leaf nodes prior to the traversal of
    first (i.e., leftmost) descendant is marked.

    A topological sort will be applied if `phylogeny_df` is not topologically
    sorted. Dataframe reindexing (e.g., df.index) may be applied.

    Must be a strictly bifurcating tree.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not alifestd_is_strictly_bifurcating_asexual(phylogeny_df):
        raise ValueError("phylogeny_df must be strictly bifurcating")

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    if "num_leaves" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_num_leaves_asexual(
            phylogeny_df, mutate=True
        )

    if "is_right_child" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_is_right_child_asexual(
            phylogeny_df, mutate=True
        )

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df[
            "num_preceding_leaves"
        ] = _alifestd_mark_num_preceding_leaves_asexual_fast_path(
            phylogeny_df["ancestor_id"].to_numpy(),
            phylogeny_df["num_leaves"].to_numpy(),
            phylogeny_df["is_right_child"].to_numpy(),
        )
        return phylogeny_df
    else:
        return _alifestd_mark_num_preceding_leaves_asexual_slow_path(
            phylogeny_df,
        )
