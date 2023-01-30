import typing

import ordered_set as ods
import pandas as pd

from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids


def alifestd_find_leaf_ids(phylogeny_df: pd.DataFrame) -> typing.List[int]:
    """What ids are not listed in any `ancestor_list`?"""
    all_ids = ods.OrderedSet(phylogeny_df["id"])

    internal_ids = (
        set(
            ancestor_id
            for ancestor_list_str in phylogeny_df["ancestor_list"]
            for ancestor_id in alifestd_parse_ancestor_ids(ancestor_list_str)
        )
        if "ancestor_id" not in phylogeny_df
        else set(
            # root is self ref, but must exclude to handle only-root phylo
            phylogeny_df.loc[
                phylogeny_df["ancestor_id"] != phylogeny_df["id"],
                "ancestor_id",
            ]
        )
    )
    return list(all_ids - internal_ids)
