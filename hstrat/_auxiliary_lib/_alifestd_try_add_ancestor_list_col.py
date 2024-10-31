import pandas as pd

from ._alifestd_make_ancestor_list_col import alifestd_make_ancestor_list_col


def alifestd_try_add_ancestor_list_col(
    phylogeny_df: pd.DataFrame,
    root_ancestor_token: str = "none",
    mutate: bool = False,
) -> pd.DataFrame:
    """Add an ancestor_list column to the input DataFrame if the column does
    not already exist.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.

    See Also
    --------
    alifestd_make_ancestor_list_col
    """

    if "ancestor_id" in phylogeny_df and "ancestor_list" not in phylogeny_df:
        if not mutate:
            phylogeny_df = phylogeny_df.copy()
        phylogeny_df["ancestor_list"] = alifestd_make_ancestor_list_col(
            phylogeny_df["id"],
            phylogeny_df["ancestor_id"],
            root_ancestor_token=root_ancestor_token,
        )

    return phylogeny_df
