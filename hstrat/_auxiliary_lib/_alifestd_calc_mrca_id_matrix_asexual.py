import typing

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
    *,
    progress_wrap: typing.Callable = lambda x: x,
) -> np.ndarray:
    """Calculate the Most Recent Common Ancestor (MRCA) taxon id for each pair
    of taxa.

    Taxa sharing no common ancestor will have MRCA id -1.

    Pass tqdm or equivalent as `progress_wrap` to display a progress bar.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not alifestd_is_working_format_asexual(phylogeny_df, mutate=True):
        raise NotImplementedError(
            "current implementation requires phylogeny_df in working format",
        )

    phylogeny_df = alifestd_mark_node_depth_asexual(phylogeny_df, mutate=True)

    n = len(phylogeny_df)
    result = -np.ones((n, n), dtype=np.int64)
    if n == 0:
        return result

    max_depth = int(phylogeny_df["node_depth"].max())

    ancestor_ids = phylogeny_df["ancestor_id"].to_numpy()
    node_depths = phylogeny_df["node_depth"].to_numpy()
    cur_positions = phylogeny_df["id"].to_numpy().copy()
    assert np.all(cur_positions == np.arange(len(phylogeny_df)))

    for depth in progress_wrap(reversed(range(max_depth + 1))):
        depth_mask = node_depths[cur_positions] == depth

        ansatz = -np.ones_like(result)

        ansatz[:, depth_mask] = cur_positions[depth_mask]
        ansatz[depth_mask, :] = cur_positions[depth_mask, None]
        ansatz[~depth_mask, :] = -1
        ansatz[:, ~depth_mask] = -1

        ansatz[ansatz != ansatz.T] = -1

        result = np.maximum(result, ansatz)
        cur_positions[depth_mask] = ancestor_ids[cur_positions[depth_mask]]

    return result
