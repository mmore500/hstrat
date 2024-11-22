import numpy as np
import pandas as pd


def alifestd_count_root_nodes(phylogeny_df: pd.DataFrame) -> np.ndarray:  # int
    """How many root nodes are contained in phylogeny?"""
    return (
        phylogeny_df["ancestor_list"]
        .astype(str)
        .str.lower()
        .isin(("[none]", "[]"))
        .sum()
    )
