import typing

import ordered_set as ods
import pandas as pd

from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids


def alifestd_find_leaf_ids(phylogeny_df: pd.DataFrame) -> typing.List[int]:
    all_ids = ods.OrderedSet(phylogeny_df["id"])
    internal_ids = set(
        ancestor_id
        for ancestor_list_str in phylogeny_df["ancestor_list"]
        for ancestor_id in alifestd_parse_ancestor_ids(ancestor_list_str)
    )
    return list(all_ids - internal_ids)
