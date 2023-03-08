import pandas as pd


def alifestd_has_multiple_roots(phylogeny_df: pd.DataFrame) -> bool:
    """Does the phylogeny two or more root organisms?

    Input dataframe is not mutated by this operation.
    """
    return (
        (phylogeny_df["ancestor_list"] == "[]").sum()
        + (phylogeny_df["ancestor_list"] == "[NONE]").sum()
        + (phylogeny_df["ancestor_list"] == "[none]").sum()
        + (phylogeny_df["ancestor_list"] == "[None]").sum()
    ) >= 2
