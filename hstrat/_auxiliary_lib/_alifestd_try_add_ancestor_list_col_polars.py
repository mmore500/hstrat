import logging

import polars as pl

from ._alifestd_make_ancestor_list_col_polars import (
    alifestd_make_ancestor_list_col_polars,
)


def alifestd_try_add_ancestor_list_col_polars(
    phylogeny_df: pl.DataFrame,
    root_ancestor_token: str = "none",
    mutate: bool = False,
) -> pl.DataFrame:
    """Add an ancestor_list column to the input DataFrame if the column does
    not already exist.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.

    Notes
    -----
    Even allowed by `mutate` flag, no side effects occur on input dataframe
    under Polars implementation. Flag is included for API compatibility with
    Pandas implementation.

    See Also
    --------
    alifestd_make_ancestor_list_col
    """
    if "ancestor_id" in phylogeny_df and "ancestor_list" not in phylogeny_df:
        logging.info("ancestor_id column present, adding ancestor_list column")
        return phylogeny_df.with_columns(
            alifestd_make_ancestor_list_col_polars(
                phylogeny_df["id"],
                phylogeny_df["ancestor_id"],
                root_ancestor_token=root_ancestor_token,
            ).alias("ancestor_list")
        )
    elif "ancestor_list" in phylogeny_df:
        logging.info("ancestor_list column already present, skipping addition")
    else:
        logging.info(
            "no ancestor_id column available, skipping ancestor_list addition",
        )

    return phylogeny_df
