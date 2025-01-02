import numpy as np
import pandas as pd


def alifestd_find_root_ids(phylogeny_df: pd.DataFrame) -> np.ndarray:  # int
    """What ids have an empty `ancestor_list`?

    Input dataframe is not mutated by this operation.
    """

    root_mask = (
        (phylogeny_df["ancestor_id"] == phylogeny_df["id"])
        if "ancestor_id" in phylogeny_df
        else (
            phylogeny_df["ancestor_list"]
            .astype(str)
            .str.lower()
            .isin(("[none]", "[]"))
        )
    )

    return phylogeny_df.loc[root_mask, "id"].to_numpy().copy()
