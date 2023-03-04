import numpy as np
import pandas as pd


def alifestd_find_root_ids(phylogeny_df: pd.DataFrame) -> np.array:  # int
    """What ids have an empty `ancestor_list`?

    Input dataframe is not mutated by this operation.
    """

    root_df = phylogeny_df[
        phylogeny_df["ancestor_list"].str.lower().isin(("[none]", "[]"))
    ]
    return root_df["id"].to_numpy().copy()
