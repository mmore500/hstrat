import pandas as pd


def alifestd_is_sexual(phylogeny_df: pd.DataFrame) -> bool:
    """Do any organisms in the phylogeny have than one immediate ancestor?"""
    return phylogeny_df["ancestor_list"].str.contains(",").any()
