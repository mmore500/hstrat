import pandas as pd

from ._alifestd_is_asexual import alifestd_is_asexual
from ._alifestd_make_ancestor_id_col import alifestd_make_ancestor_id_col


def alifestd_try_add_ancestor_id_col(
    phylogeny_df: pd.DataFrame,
) -> pd.DataFrame:
    if alifestd_is_asexual(phylogeny_df) and "ancestor_id" not in phylogeny_df:
        phylogeny_df = phylogeny_df.copy()
        phylogeny_df["ancestor_id"] = alifestd_make_ancestor_id_col(
            phylogeny_df["id"], phylogeny_df["ancestor_list"]
        )

    return phylogeny_df
