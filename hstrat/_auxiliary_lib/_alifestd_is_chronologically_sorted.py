import pandas as pd


def alifestd_is_chronologically_sorted(
    phylogeny_df: pd.DataFrame,
    how: str = "origin_time",
) -> bool:
    """Do rows appear in chronological order?

    Defaults to `origin_time`. Input dataframe is not mutated by this operation.
    """

    return how in phylogeny_df and phylogeny_df[how].is_monotonic_increasing
