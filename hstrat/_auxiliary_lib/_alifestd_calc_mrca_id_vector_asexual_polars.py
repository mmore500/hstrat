import logging
import typing

import numpy as np
import polars as pl

from ._alifestd_calc_mrca_id_vector_asexual import (
    _alifestd_calc_mrca_id_vector_asexual_fast_path,
)
from ._alifestd_has_contiguous_ids_polars import (
    alifestd_has_contiguous_ids_polars,
)
from ._alifestd_is_topologically_sorted_polars import (
    alifestd_is_topologically_sorted_polars,
)
from ._alifestd_try_add_ancestor_id_col_polars import (
    alifestd_try_add_ancestor_id_col_polars,
)


def alifestd_calc_mrca_id_vector_asexual_polars(
    phylogeny_df: pl.DataFrame,
    *,
    target_id: int,
    progress_wrap: typing.Callable = lambda x: x,
) -> np.ndarray:
    """Calculate the Most Recent Common Ancestor (MRCA) taxon id for
    target_id and each other taxon.

    Taxa sharing no common ancestor will have MRCA id -1.

    Parameters
    ----------
    phylogeny_df : polars.DataFrame or polars.LazyFrame
        The phylogeny as a dataframe in alife standard format.

        Must represent an asexual phylogeny in working format (i.e.,
        topologically sorted with contiguous ids and an ancestor_id
        column, or an ancestor_list column from which ancestor_id can
        be derived).
    target_id : int
        The target organism id to compute MRCA against.
    progress_wrap : callable, optional
        Wrapper for progress display (e.g., tqdm).

    Returns
    -------
    numpy.ndarray
        Array of shape (n,) with dtype int64, containing MRCA ids for
        each organism with the target.  Entries are -1 where organisms
        share no common ancestor with the target.

    See Also
    --------
    alifestd_calc_mrca_id_vector_asexual :
        Pandas-based implementation.
    """
    logging.info(
        "- alifestd_calc_mrca_id_vector_asexual_polars: "
        "adding ancestor_id col...",
    )
    phylogeny_df = alifestd_try_add_ancestor_id_col_polars(phylogeny_df)

    logging.info(
        "- alifestd_calc_mrca_id_vector_asexual_polars: "
        "checking contiguous ids...",
    )
    if not alifestd_has_contiguous_ids_polars(phylogeny_df):
        raise NotImplementedError(
            "non-contiguous ids not yet supported",
        )

    logging.info(
        "- alifestd_calc_mrca_id_vector_asexual_polars: "
        "checking topological sort...",
    )
    if not alifestd_is_topologically_sorted_polars(phylogeny_df):
        raise NotImplementedError(
            "topologically unsorted rows not yet supported",
        )

    logging.info(
        "- alifestd_calc_mrca_id_vector_asexual_polars: "
        "extracting ancestor ids...",
    )
    ancestor_ids = (
        phylogeny_df.lazy()
        .select("ancestor_id")
        .collect()
        .to_series()
        .to_numpy()
        .astype(np.int64)
    )

    n = len(ancestor_ids)
    if target_id >= n:
        raise ValueError(f"{target_id=} out of bounds")
    assert n

    logging.info(
        "- alifestd_calc_mrca_id_vector_asexual_polars: "
        "computing mrca ids...",
    )
    return _alifestd_calc_mrca_id_vector_asexual_fast_path(
        ancestor_ids, target_id
    )
