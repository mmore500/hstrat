import typing

import pandas as pd

from ._alifestd_check_topological_sensitivity import (
    alifestd_check_topological_sensitivity,
)


def alifestd_drop_topological_sensitivity(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Drop columns from `phylogeny_df` that may be invalidated by
    topological operations such as collapsing unifurcations.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """
    to_drop = alifestd_check_topological_sensitivity(phylogeny_df)
    if not to_drop:
        return phylogeny_df

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df.drop(columns=to_drop, inplace=True)
    return phylogeny_df
