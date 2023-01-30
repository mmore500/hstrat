from collections import Counter

import pandas as pd

from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids
from ._alifestd_topological_sort import alifestd_topological_sort


def alifestd_collapse_unifurcations(
    phylogeny_df: pd.DataFrame,
) -> pd.DataFrame:
    """Pare record to bypass organisms with one ancestor and one descendant."""

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df)

    phylogeny_df = phylogeny_df.set_index("id", drop=False)

    ref_counts = Counter(
        id
        for ancestor_list_str in phylogeny_df["ancestor_list"]
        for id in alifestd_parse_ancestor_ids(ancestor_list_str)
    )

    for id in phylogeny_df["id"]:
        ancestor_ids = alifestd_parse_ancestor_ids(
            phylogeny_df.loc[id, "ancestor_list"]
        )
        if len(ancestor_ids) == 1 and ref_counts[id] == 1:
            # percolate ancestor over self
            (ancestor_id,) = ancestor_ids
            phylogeny_df.loc[id] = phylogeny_df.loc[ancestor_id]
        elif len(ancestor_ids):
            # update referenced ancestor
            phylogeny_df.loc[id, "ancestor_list"] = str(
                [
                    phylogeny_df.loc[ancestor_id, "id"]
                    for ancestor_id in ancestor_ids
                ]
            )

    return phylogeny_df.drop_duplicates().reset_index(drop=True)
