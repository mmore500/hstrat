import pandas as pd


def alifestd_has_compact_ids(phylogeny_df: pd.DataFrame) -> bool:
    """Are id values between 0 and `len(phylogeny_df)`, in any order?

    Input dataframe is not mutated by this operation.
    """
    return len(phylogeny_df) == 0 or (
        phylogeny_df["id"].max() == len(phylogeny_df) - 1
    )
