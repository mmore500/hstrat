import pandas as pd

from ._alifestd_find_root_ids import alifestd_find_root_ids
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids


def alifestd_mark_roots(
    phylogeny_df: pd.DataFrame, mutate: bool = False
) -> pd.DataFrame:
    """Create column `is_root` to mark rows with no ancestor.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    root_ids = alifestd_find_root_ids(phylogeny_df)
    phylogeny_df["is_root"] = False
    phylogeny_df.loc[root_ids, "is_root"] = True

    return phylogeny_df
