import pandas as pd


def alifestd_has_compact_ids(phylogeny_df: pd.DataFrame) -> bool:
    """TODO"""
    return len(phylogeny_df) == 0 or (
        phylogeny_df["id"].max() == len(phylogeny_df) - 1
    )
