from collections import Counter

import pandas as pd

from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids
from ._alifestd_try_add_ancestor_list_col import (
    alifestd_try_add_ancestor_list_col,
)


def alifestd_topological_sort(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Sort rows so all organisms follow members of their `ancestor_list`.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    has_ancestor_list = "ancestor_list" in phylogeny_df
    if not has_ancestor_list:
        phylogeny_df = alifestd_try_add_ancestor_list_col(
            phylogeny_df, mutate=True
        )

    phylogeny_df.set_index("id", drop=False, inplace=True)

    unsorted_ids = set(phylogeny_df["id"])
    internal_ids_refcounts = Counter(
        id
        for ancestor_list_str in phylogeny_df["ancestor_list"]
        for id in alifestd_parse_ancestor_ids(ancestor_list_str)
    )
    internal_ids_set = set(internal_ids_refcounts.keys())

    reverse_sorted_ids = []
    while unsorted_ids:
        leaf_ids = unsorted_ids - internal_ids_set
        reverse_sorted_ids.extend(leaf_ids)
        unsorted_ids -= leaf_ids

        leaf_parent_counts = Counter(
            id
            for ancestor_list_str in phylogeny_df.loc[[*leaf_ids]][
                "ancestor_list"
            ]
            for id in alifestd_parse_ancestor_ids(ancestor_list_str)
        )
        internal_ids_refcounts.subtract(leaf_parent_counts)

        for leaf_parent_id in leaf_parent_counts.keys():
            refcount = internal_ids_refcounts[leaf_parent_id]
            assert refcount >= 0
            if refcount == 0:
                internal_ids_set.remove(leaf_parent_id)
                del internal_ids_refcounts[leaf_parent_id]

    assert set(reverse_sorted_ids) == set(phylogeny_df["id"])
    res = phylogeny_df.loc[reverse_sorted_ids[::-1], :].reset_index(drop=True)

    if not has_ancestor_list:
        res.drop(columns=["ancestor_list"], inplace=True)

    return res
