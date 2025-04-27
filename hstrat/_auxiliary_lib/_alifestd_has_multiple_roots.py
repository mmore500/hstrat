import pandas as pd


def alifestd_has_multiple_roots(phylogeny_df: pd.DataFrame) -> bool:
    """Does the phylogeny two or more root organisms?

    Input dataframe is not mutated by this operation.
    """
    if "ancestor_id" in phylogeny_df.columns:
        return (phylogeny_df["ancestor_id"] == phylogeny_df["id"]).sum() >= 2
    else:
        return (
            (phylogeny_df["ancestor_list"] == "[]").sum()
            + (phylogeny_df["ancestor_list"] == "[NONE]").sum()
            + (phylogeny_df["ancestor_list"] == "[none]").sum()
            + (phylogeny_df["ancestor_list"] == "[None]").sum()
        ) >= 2
