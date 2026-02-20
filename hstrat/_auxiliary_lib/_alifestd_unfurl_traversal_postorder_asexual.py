import numpy as np
import pandas as pd

from ._alifestd_mark_node_depth_asexual import (
    _alifestd_calc_node_depth_asexual_contiguous,
    alifestd_mark_node_depth_asexual,
)
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def _unfurl_traversal_postorder_asexual_contiguous(
    ancestor_ids: np.ndarray,
) -> np.ndarray:
    """Return postorder traversal indices for contiguous, sorted phylogeny.

    Parameters
    ----------
    ancestor_ids : np.ndarray
        Array of ancestor IDs, assumed contiguous (ids == row indices)
        and topologically sorted.

    Returns
    -------
    np.ndarray
        Index array giving postorder traversal order.
    """
    node_depths = _alifestd_calc_node_depth_asexual_contiguous(ancestor_ids)
    return np.lexsort((ancestor_ids, node_depths))[::-1]


def alifestd_unfurl_traversal_postorder_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> np.ndarray:
    """List `id` values in postorder traversal order.

    The provided dataframe must be asexual.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)
    phylogeny_df = alifestd_mark_node_depth_asexual(phylogeny_df, mutate=True)
    postorder_index = np.lexsort(
        (phylogeny_df["ancestor_id"], phylogeny_df["node_depth"]),
    )[::-1]
    id_loc = phylogeny_df.columns.get_loc("id")
    return phylogeny_df.iloc[postorder_index, id_loc].to_numpy()
