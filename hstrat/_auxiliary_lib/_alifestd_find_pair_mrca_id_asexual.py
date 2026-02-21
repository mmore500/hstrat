import typing

import numpy as np
import opytional as opyt
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._jit import jit


@jit(nopython=True)
def _alifestd_find_pair_mrca_id_asexual_fast_path(
    ancestor_ids: np.ndarray,
    first: int,
    second: int,
) -> int:
    """Find the MRCA of two taxa in a contiguous, topologically sorted
    asexual phylogeny.

    Parameters
    ----------
    ancestor_ids : np.ndarray
        Array of ancestor ids, where index corresponds to taxon id.

        Must be topologically sorted with contiguous ids.
    first : int
        First taxon id.
    second : int
        Second taxon id.

    Returns
    -------
    int
        The id of the most recent common ancestor, or -1 if no common
        ancestor exists.
    """
    ancestor_ids = ancestor_ids.astype(np.uint64)
    # walk both lineages towards the root, always advancing the deeper
    # (higher-id) node first; when both reach the same node, that is
    # the MRCA
    a = first
    b = second
    while a != b:
        if a > b:
            next_a = ancestor_ids[a]
            if next_a == a:
                # a is a root; walk b up to see if it reaches a
                while b != a:
                    next_b = ancestor_ids[b]
                    if next_b == b:
                        return -1  # b is also a root, disjoint trees
                    b = next_b
                return a
            a = next_a
        else:
            next_b = ancestor_ids[b]
            if next_b == b:
                # b is a root; walk a up to see if it reaches b
                while a != b:
                    next_a = ancestor_ids[a]
                    if next_a == a:
                        return -1  # a is also a root, disjoint trees
                    a = next_a
                return b
            b = next_b
    return a


def alifestd_find_pair_mrca_id_asexual(
    phylogeny_df: pd.DataFrame,
    first: int,
    second: int,
    *,
    mutate: bool = False,
    is_topologically_sorted: typing.Optional[bool] = None,
    has_contiguous_ids: typing.Optional[bool] = None,
) -> typing.Optional[int]:
    """Find the Most Recent Common Ancestor of two taxa.

    Parameters
    ----------
    phylogeny_df : pd.DataFrame
        Phylogeny in alife standard format.
    first : int
        First taxon id.
    second : int
        Second taxon id.
    mutate : bool, default False
        If True, allows in-place modification of `phylogeny_df`.
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
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)
    if "ancestor_id" not in phylogeny_df.columns:
        raise ValueError(
            "alifestd_find_pair_mrca_id_asexual requires ancestor_id column",
        )

    if not opyt.or_else(
        is_topologically_sorted,
        lambda: alifestd_is_topologically_sorted(phylogeny_df),
    ):
        raise NotImplementedError(
            "topologically unsorted rows not yet supported",
        )

    if not opyt.or_else(
        has_contiguous_ids,
        lambda: alifestd_has_contiguous_ids(phylogeny_df),
    ):
        raise NotImplementedError(
            "non-contiguous ids not yet supported",
        )

    ancestor_ids = phylogeny_df["ancestor_id"].to_numpy()
    result = _alifestd_find_pair_mrca_id_asexual_fast_path(
        ancestor_ids, first, second,
    )
    return None if result == -1 else int(result)
