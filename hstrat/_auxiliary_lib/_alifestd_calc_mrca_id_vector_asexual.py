import logging
import typing

import numpy as np
import pandas as pd

from ._alifestd_is_working_format_asexual import (
    alifestd_is_working_format_asexual,
)
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._jit import jit


@jit(nopython=True)
def _alifestd_calc_mrca_id_vector_asexual_fast_path(
    ancestor_ids: np.ndarray,
    target_id: int,
) -> np.ndarray:
    """Implementation detail for
    `alifestd_calc_mrca_id_vector_asexual`."""
    ancestor_ids = ancestor_ids.astype(np.int64)
    n = len(ancestor_ids)
    assert n > 0

    mrca_ids = ancestor_ids.copy()

    # Mark roots (self-ancestors) as -1
    for i in range(n):
        if ancestor_ids[i] == i:
            mrca_ids[i] = np.int64(-1)

    # Pass 1: Target Lineage Tracing
    curr = np.int64(target_id)
    while ancestor_ids[curr] != curr:
        mrca_ids[curr] = curr
        curr = np.int64(ancestor_ids[curr])
    mrca_ids[curr] = curr

    # Pass 2: Left-to-Right MRCA Propagation
    for i in range(n):
        if mrca_ids[i] != i:
            parent = np.int64(ancestor_ids[i])
            mrca_ids[i] = mrca_ids[parent]

    return mrca_ids


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

    logging.info(
        "- alifestd_calc_mrca_id_vector_asexual: " "adding ancestor_id col...",
    )
    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not alifestd_is_working_format_asexual(phylogeny_df, mutate=True):
        raise NotImplementedError(
            "current implementation requires phylogeny_df in working format",
        )

    if target_id >= len(phylogeny_df):
        raise ValueError(f"{target_id=} out of bounds")

    ancestor_ids = phylogeny_df["ancestor_id"].to_numpy()
    assert np.all(
        phylogeny_df["id"].to_numpy() == np.arange(len(phylogeny_df))
    )

    logging.info(
        "- alifestd_calc_mrca_id_vector_asexual: computing mrca ids...",
    )
    return _alifestd_calc_mrca_id_vector_asexual_fast_path(
        ancestor_ids, target_id
    )
