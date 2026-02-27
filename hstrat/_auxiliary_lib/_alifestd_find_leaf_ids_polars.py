import logging

import numpy as np
import polars as pl

from ._alifestd_has_contiguous_ids_polars import (
    alifestd_has_contiguous_ids_polars,
)
from ._alifestd_mark_num_children_asexual import (
    _alifestd_mark_num_children_asexual_fast_path,
)


def alifestd_find_leaf_ids_polars(
    phylogeny_df: pl.DataFrame,
) -> np.ndarray:
    """What ids are ancestor to no other ids?


    Parameters
    ----------
    phylogeny_df : polars.DataFrame or polars.LazyFrame
        The phylogeny as a dataframe in alife standard format.

        Must have contiguous ids and represent an asexual phylogeny.

    Returns
    -------
    numpy.ndarray
        Array of leaf node ids.

    See Also
    --------
    alifestd_find_leaf_ids :
        Pandas-based implementation.
    """
    logging.info(
        "- alifestd_find_leaf_ids_polars: checking contiguous ids...",
    )
    if not alifestd_has_contiguous_ids_polars(phylogeny_df):
        raise NotImplementedError("non-contiguous ids not yet supported")

    logging.info(
        "- alifestd_find_leaf_ids_polars: extracting ancestor ids...",
    )
    ancestor_ids = (
        phylogeny_df.lazy()
        .select("ancestor_id")
        .collect()
        .to_series()
        .to_numpy()
    )

    logging.info(
        "- alifestd_find_leaf_ids_polars: tabulating child counts...",
    )
    child_counts = _alifestd_mark_num_children_asexual_fast_path(ancestor_ids)

    logging.info(
        "- alifestd_find_leaf_ids_polars: finding leaf ids...",
    )
    return np.flatnonzero(child_counts == 0)
