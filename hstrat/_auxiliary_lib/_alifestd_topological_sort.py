from collections import Counter

import pandas as pd

from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids


def alifestd_topological_sort(phylogeny_df: pd.DataFrame) -> pd.DataFrame:

    phylogeny_df = phylogeny_df.set_index("id", drop=False)

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

    return phylogeny_df.loc[reverse_sorted_ids[::-1], :].reset_index(drop=True)
