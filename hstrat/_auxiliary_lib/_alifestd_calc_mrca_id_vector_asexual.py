import typing

import numpy as np
import pandas as pd

from ._alifestd_is_working_format_asexual import (
    alifestd_is_working_format_asexual,
)
from ._alifestd_mark_node_depth_asexual import alifestd_mark_node_depth_asexual
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def _calc_mrca_id_vector_from_numpy(
    ancestor_ids: np.ndarray,
    node_depths: np.ndarray,
    target_id: int,
    progress_wrap: typing.Callable = lambda x: x,
) -> np.ndarray:
    """Core MRCA vector calculation operating on numpy arrays.

    Parameters
    ----------
    ancestor_ids : numpy.ndarray
        Array of ancestor ids, indexed by contiguous organism id.
    node_depths : numpy.ndarray
        Array of node depths, indexed by contiguous organism id.
    target_id : int
        The target organism id to compute MRCA against.
    progress_wrap : callable, optional
        Wrapper for progress display (e.g., tqdm).

    Returns
    -------
    numpy.ndarray
        Array of MRCA ids for each organism with the target.
    """
    n = len(ancestor_ids)
    assert n
    result = -np.ones(n, dtype=np.int64)

    max_depth = int(node_depths.max())

    cur_positions = np.arange(n)
    target_depth = node_depths[target_id]

    for depth in progress_wrap(reversed(range(max_depth + 1))):
        if depth <= target_depth:
            target_position = cur_positions[target_id]
            result = np.maximum(
                result,
                np.where(
                    cur_positions == target_position,
                    target_position,
                    -1,
                ),
            )

        depth_mask = node_depths[cur_positions] == depth
        cur_positions[depth_mask] = ancestor_ids[cur_positions[depth_mask]]

    return result


def alifestd_calc_mrca_id_vector_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    *,
    target_id: int,
    progress_wrap: typing.Callable = lambda x: x,
) -> np.ndarray:
    """Calculate the Most Recent Common Ancestor (MRCA) taxon id for target_id
    and each other taxon.

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

    if target_id >= len(phylogeny_df):
        raise ValueError(f"{target_id=} out of bounds")

    ancestor_ids = phylogeny_df["ancestor_id"].to_numpy()
    node_depths = phylogeny_df["node_depth"].to_numpy()
    assert np.all(
        phylogeny_df["id"].to_numpy() == np.arange(len(phylogeny_df))
    )

    return _calc_mrca_id_vector_from_numpy(
        ancestor_ids, node_depths, target_id, progress_wrap
    )
