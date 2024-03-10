import typing

import pandas as pd
import sortedcontainers as sc

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_mark_num_descendants_asexual import (
    alifestd_mark_num_descendants_asexual,
)
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_categorize_triplet_asexual(
    phylogeny_df: pd.DataFrame,
    triplet_ids: typing.Iterable[int],
    mutate: bool = False,
) -> int:
    """Assess the topological configuration of three `id`'s in `phylogeny_df`.

    If polytomy, return -1. Else, return index of outgroup `id`.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.

    See Also
    --------
    alifestd_estimate_triplet_distance_asexual
    alifestd_sample_triplet_comparisons_asexual
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

    trace = [*triplet_ids]
    queue = sc.SortedSet(trace, key=phylogeny_df.index.get_loc)
    if not len(queue) == 3:
        raise ValueError(
            "triplet_ids should have 3 unique values, "
            f"but only has {len(queue)}.",
        )

    while len(queue) == 3 or trace.count(queue[-1]) == 1:
        assert len(queue) >= 2
        oldest = queue.pop(-1)
        replacement = phylogeny_df.at[oldest, "ancestor_id"]
        assert replacement != oldest
        queue.add(replacement)
        trace[trace.index(oldest)] = replacement

    counts = [*map(trace.count, trace)]
    assert counts.count(1) <= 1
    try:
        return counts.index(1)
    except ValueError:
        return -1
