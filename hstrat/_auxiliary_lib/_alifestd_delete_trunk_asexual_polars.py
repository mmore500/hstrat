import logging

import pandas as pd
import polars as pl

from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_delete_trunk_asexual_polars(
    phylogeny_df: pd.DataFrame,
) -> pd.DataFrame:
    """Delete entries masked by `is_trunk` column.

    Masked entries must be contiguous, meaning that no non-trunk entry can
    be an ancestor of a trunk entry. Children of deleted entries will become
    roots.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.

    See Also
    --------
    alifestd_collapse_trunk_asexual
    """
    if "is_trunk" not in phylogeny_df:
        raise ValueError(
            "`is_trunk` column not provided, trunk is unspecified"
        )

    if "ancestor_list" in phylogeny_df:
        raise NotImplementedError

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    has_contiguous_ids = phylogeny_df.select(
        pl.col("id").diff() == 1
    ).to_series().all() and (phylogeny_df["id"].first() == 0)
    if not has_contiguous_ids:
        raise NotImplementedError("non-contiguous ids not yet supported")

    logging.info(
        "- alifestd_delete_trunk_asexual_polars: marking ancestor_is_trunk...",
    )
    phylogeny_df = phylogeny_df.with_columns(
        ancestor_is_trunk=pl.col("is_trunk").gather(
            pl.col("ancestor_id"),
        )
    )

    logging.info(
        "- alifestd_delete_trunk_asexual_polars: testing special cases..."
    )
    if (phylogeny_df["is_trunk"] & ~phylogeny_df["ancestor_is_trunk"]).any():
        raise ValueError("specified trunk is non-contiguous")

    if phylogeny_df["is_trunk"].sum() == 0:
        return phylogeny_df

    logging.info(
        "- alifestd_delete_trunk_asexual_polars: updating ancestor_id...",
    )
    phylogeny_df = phylogeny_df.with_columns(
        ancestor_id=pl.when(pl.col("ancestor_is_trunk"))
        .then(pl.col("id"))
        .otherwise(pl.col("ancestor_id")),
    )

    logging.info("- alifestd_delete_trunk_asexual_polars: filtering...")
    phylogeny_df = phylogeny_df.filter(~pl.col("is_trunk"))

    assert phylogeny_df["is_trunk"].sum() == 0
    return phylogeny_df
