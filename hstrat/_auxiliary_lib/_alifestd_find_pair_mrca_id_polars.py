import typing

import opytional as opyt
import polars as pl

from ._alifestd_find_pair_mrca_id_asexual import (
    _alifestd_find_pair_mrca_id_asexual_fast_path,
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


def alifestd_find_pair_mrca_id_polars(
    phylogeny_df: pl.DataFrame,
    first: int,
    second: int,
    *,
    is_topologically_sorted: typing.Optional[bool] = None,
    has_contiguous_ids: typing.Optional[bool] = None,
) -> typing.Optional[int]:
    """Find the Most Recent Common Ancestor of two taxa.

    Parameters
    ----------
    phylogeny_df : polars.DataFrame or polars.LazyFrame
        The phylogeny as a dataframe in alife standard format.

        Must represent an asexual phylogeny with contiguous ids and
        topologically sorted rows.
    first : int
        First taxon id.
    second : int
        Second taxon id.
    is_topologically_sorted : bool, optional
        If provided, skips the topological sort check. If None
        (default), the check is performed automatically.
    has_contiguous_ids : bool, optional
        If provided, skips the contiguous ids check. If None (default),
        the check is performed automatically.

    Returns
    -------
    int or None
        The id of the most recent common ancestor, or None if no common
        ancestor exists.

    See Also
    --------
    alifestd_find_pair_mrca_id_asexual :
        Pandas-based implementation.
    """
    phylogeny_df = alifestd_try_add_ancestor_id_col_polars(phylogeny_df)

    if not opyt.or_else(
        has_contiguous_ids,
        lambda: alifestd_has_contiguous_ids_polars(phylogeny_df),
    ):
        raise NotImplementedError(
            "non-contiguous ids not yet supported",
        )

    if not opyt.or_else(
        is_topologically_sorted,
        lambda: alifestd_is_topologically_sorted_polars(phylogeny_df),
    ):
        raise NotImplementedError(
            "topologically unsorted rows not yet supported",
        )

    ancestor_ids = (
        phylogeny_df.lazy()
        .select("ancestor_id")
        .collect()
        .to_series()
        .to_numpy()
    )

    result = _alifestd_find_pair_mrca_id_asexual_fast_path(
        ancestor_ids,
        first,
        second,
    )
    return None if result == -1 else int(result)
