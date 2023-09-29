import pandas as pd


def alifestd_chronological_sort(
    phylogeny_df: pd.DataFrame,
    how: str = "origin_time",
    mutate: bool = False,
) -> pd.DataFrame:
    """Sort rows so all organisms appear in chronological order, default
    `origin_time`.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df.sort_values(by=how, inplace=True)
    phylogeny_df.reset_index(drop=True, inplace=True)
    return phylogeny_df
