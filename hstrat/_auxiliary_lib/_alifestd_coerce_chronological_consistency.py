import pandas as pd

from ._alifestd_find_chronological_inconsistency import (
    alifestd_find_chronological_inconsistency,
)
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids
from ._alifestd_topological_sort import alifestd_topological_sort


def alifestd_coerce_chronological_consistency(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """For any taxa with origin time preceding its parent's, set origin time
    to parent's origin time.

    If an inconsistency is detected, the corrected phylogeny will be returned
    sorted in topological order.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if (
        not alifestd_is_topologically_sorted(phylogeny_df)
        and alifestd_find_chronological_inconsistency(phylogeny_df) is not None
    ):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    phylogeny_df = phylogeny_df.set_index("id", drop=False)

    # adapted from https://stackoverflow.com/a/31569794
    origin_time_loc = phylogeny_df.columns.get_loc("origin_time")
    for pos, (_idx, row) in enumerate(phylogeny_df.iterrows()):
        for ancestor_id in alifestd_parse_ancestor_ids(row["ancestor_list"]):
            ancestor_loc = phylogeny_df.index.get_loc(ancestor_id)
            ancestor_time = phylogeny_df.iat[ancestor_loc, origin_time_loc]
            offspring_time = phylogeny_df.iat[pos, origin_time_loc]
            phylogeny_df.iat[pos, origin_time_loc] = max(
                offspring_time, ancestor_time
            )

    return phylogeny_df
