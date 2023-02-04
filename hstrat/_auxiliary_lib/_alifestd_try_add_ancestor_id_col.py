import pandas as pd

from ._alifestd_is_asexual import alifestd_is_asexual
from ._alifestd_make_ancestor_id_col import alifestd_make_ancestor_id_col


def alifestd_try_add_ancestor_id_col(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add an ancestor_id column to the input DataFrame if the phylogeny is
    asexual and the column does not already exist.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if alifestd_is_asexual(phylogeny_df) and "ancestor_id" not in phylogeny_df:
        if not mutate:
            phylogeny_df = phylogeny_df.copy()
        phylogeny_df["ancestor_id"] = alifestd_make_ancestor_id_col(
            phylogeny_df["id"], phylogeny_df["ancestor_list"]
        )

    return phylogeny_df
