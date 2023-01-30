import numpy as np
import pandas as pd


def alifestd_has_contiguous_ids(phylogeny_df: pd.DataFrame) -> bool:
    """TODO"""
    return (
        phylogeny_df["id"].to_numpy() == np.arange(len(phylogeny_df))
    ).all()
