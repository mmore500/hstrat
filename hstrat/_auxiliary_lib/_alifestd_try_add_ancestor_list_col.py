import pandas as pd

from ._alifestd_make_ancestor_list_col import alifestd_make_ancestor_list_col
from ._alifestd_try_add_ancestor_list_col_polars import (
    alifestd_try_add_ancestor_list_col_polars,
)
from ._delegate_polars_implementation import (
    DataFrame_T,
    delegate_polars_implementation,
)


@delegate_polars_implementation(alifestd_try_add_ancestor_list_col_polars)
def alifestd_try_add_ancestor_list_col(
    phylogeny_df: DataFrame_T,
    root_ancestor_token: str = "none",
    mutate: bool = False,
) -> DataFrame_T:
    """Add an ancestor_list column to the input DataFrame if the column does
    not already exist.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.

    See Also
    --------
    alifestd_make_ancestor_list_col
    """

    assert isinstance(phylogeny_df, pd.DataFrame)
    if "ancestor_id" in phylogeny_df and "ancestor_list" not in phylogeny_df:
        if not mutate:
            phylogeny_df = phylogeny_df.copy()
        phylogeny_df["ancestor_list"] = alifestd_make_ancestor_list_col(
            phylogeny_df["id"],
            phylogeny_df["ancestor_id"],
            root_ancestor_token=root_ancestor_token,
        )

    return phylogeny_df
