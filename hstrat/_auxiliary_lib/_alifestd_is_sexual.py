import pandas as pd


def alifestd_is_sexual(phylogeny_df: pd.DataFrame) -> bool:
    """Do any organisms in the phylogeny have than one immediate ancestor?

    Input dataframe is not mutated by this operation.
    """
    return phylogeny_df["ancestor_list"].astype("str").str.contains(",").any()
