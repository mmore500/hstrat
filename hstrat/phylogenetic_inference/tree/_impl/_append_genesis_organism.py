import pandas as pd

from ...._auxiliary_lib import alifestd_find_root_ids


def append_genesis_organism(
    alifestd_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add an entry representing the ancestor of all life organism at
    origin_time 0."""

    if not mutate:
        alifestd_df = alifestd_df.copy()

    if len(alifestd_df):
        assert alifestd_df["origin_time"].min() >= 0
        if alifestd_df["origin_time"].min() == 0:
            return alifestd_df

        genesis_id = alifestd_df["id"].max() + 1
        for old_root_id in alifestd_find_root_ids(alifestd_df):
            if "ancestor_id" in alifestd_df:
                alifestd_df.loc[
                    alifestd_df["id"] == old_root_id, "ancestor_id"
                ] = genesis_id
            alifestd_df.loc[
                alifestd_df["id"] == old_root_id, "ancestor_list"
            ] = f"[{genesis_id}]"
    else:
        genesis_id = 0

    alifestd_df = pd.concat(
        [
            alifestd_df,
            pd.DataFrame(
                {
                    "id": [genesis_id],
                    "ancestor_id": [genesis_id],
                    "origin_time": [0],
                    "ancestor_list": ["[none]"],
                    "name": "genesis",
                    "taxon_label": "genesis",
                }
            ),
        ],
        ignore_index=True,
        join="inner",
    )

    alifestd_df.reset_index(drop=True, inplace=True)

    return alifestd_df
