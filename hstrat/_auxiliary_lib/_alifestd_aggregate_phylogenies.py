import typing

import pandas as pd

from ._alifestd_make_ancestor_list_col import alifestd_make_ancestor_list_col
from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids


def alifestd_aggregate_phylogenies(
    phylogeny_dfs: typing.List[pd.DataFrame],
    mutate: bool = False,
) -> pd.DataFrame:
    """Concatenate independent phylogenies, reassigning organism ids to
    prevent collisions.

    Inputs dataframe are not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    aggregate_least_available_id = 0
    all_has_ancestor_id = all(
        "ancestor_id" in phylogeny_df for phylogeny_df in phylogeny_dfs
    )

    res = []
    for phylogeny_df in phylogeny_dfs:
        if not mutate:
            phylogeny_df = phylogeny_df.copy()
        cur_max_id = phylogeny_df["id"].max()

        if aggregate_least_available_id:
            phylogeny_df["id"] += aggregate_least_available_id
            if "ancestor_id" in phylogeny_df:
                phylogeny_df["ancestor_id"] += aggregate_least_available_id
                phylogeny_df[
                    "ancestor_list"
                ] = alifestd_make_ancestor_list_col(
                    phylogeny_df["id"], phylogeny_df["ancestor_id"]
                )
            else:
                phylogeny_df["ancestor_list"] = (
                    phylogeny_df["ancestor_list"]
                    .apply(
                        lambda ancestor_list_str: str(
                            [
                                ancestor_id + aggregate_least_available_id
                                for ancestor_id in alifestd_parse_ancestor_ids(
                                    ancestor_list_str
                                )
                            ]
                        )
                    )
                    .replace("[]", "[none]")
                )

        aggregate_least_available_id += cur_max_id + 1
        if not all_has_ancestor_id and "ancestor_id" in phylogeny_df:
            phylogeny_df.drop("ancestor_id", axis=1, inplace=True)

        res.append(phylogeny_df)

    return pd.concat(res).reset_index(drop=True)
