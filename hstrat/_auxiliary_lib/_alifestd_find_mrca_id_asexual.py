import typing

import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_mark_num_descendants_asexual import (
    alifestd_mark_num_descendants_asexual,
)
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._alifestd_unfurl_lineage_asexual import alifestd_unfurl_lineage_asexual


def alifestd_find_mrca_id_asexual(
    phylogeny_df: pd.DataFrame,
    leaf_ids: typing.Iterable[int],
    mutate: bool = False,
) -> int:
    """Find most recent common ancestor of two ids?

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    if "num_descendants" not in phylogeny_df:
        phylogeny_df = alifestd_mark_num_descendants_asexual(
            phylogeny_df, mutate=True
        )

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    lineages = [
        {*alifestd_unfurl_lineage_asexual(phylogeny_df, leaf_id, mutate=True)}
        for leaf_id in leaf_ids
    ]
    if len(lineages) == 0:
        raise ValueError()

    return min(
        set.intersection(*lineages),
        key=lambda idx: phylogeny_df.loc[idx, "num_descendants"],
    )
