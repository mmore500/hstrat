import numpy as np
import pandas as pd

from ._alifestd_is_working_format_asexual import (
    alifestd_is_working_format_asexual,
)
from ._alifestd_mark_node_depth_asexual import alifestd_mark_node_depth_asexual
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_calc_mrca_id_matrix_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> np.ndarray:
    """Calculate the Most Recent Common Ancestor (MRCA) taxon id for each pair
    of taxa."""

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not alifestd_is_working_format_asexual(phylogeny_df, mutate=True):
        raise NotImplementedError(
            "current implementation requires phylogeny_df in working format",
        )

    phylogeny_df = alifestd_mark_node_depth_asexual(phylogeny_df, mutate=True)

    n = len(phylogeny_df)
    result = np.zeros((n, n), dtype=np.uint64)
    if n == 0:
        return result

    max_depth = int(phylogeny_df["node_depth"].max())

    ancestor_ids = phylogeny_df["ancestor_id"].to_numpy()
    node_depths = phylogeny_df["node_depth"].to_numpy()
    cur_positions = phylogeny_df["id"].to_numpy().copy()
    assert np.all(cur_positions == np.arange(len(phylogeny_df)))

    for depth in reversed(range(max_depth + 1)):
        depth_mask = node_depths[cur_positions] == depth

        ansatz = np.zeros_like(result)

        ansatz[:, depth_mask] = cur_positions[depth_mask]
        ansatz[depth_mask, :] = cur_positions[depth_mask, None]
        ansatz[~depth_mask, :] = 0
        ansatz[:, ~depth_mask] = 0

        ansatz[ansatz != ansatz.T] = 0

        result = np.maximum(result, ansatz)
        cur_positions[depth_mask] = ancestor_ids[cur_positions[depth_mask]]

    return result
