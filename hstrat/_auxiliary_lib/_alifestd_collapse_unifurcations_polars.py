import logging
import warnings

import pandas as pd
import polars as pl

from ._alifestd_assign_contiguous_ids_polars import (
    alifestd_assign_contiguous_ids_polars,
)
from ._alifestd_collapse_unifurcations import _collapse_unifurcations


def alifestd_collapse_unifurcations_polars(
    phylogeny_df: pd.DataFrame,
) -> pd.DataFrame:
    """Pare record to bypass organisms with one ancestor and one descendant.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if any(
        col in phylogeny_df
        for col in ["branch_length", "edge_length", "origin_time_delta"]
    ):
        warnings.warn(
            "alifestd_collapse_unifurcations does not update branch length "
            "columns. Use `origin_time` to recalculate branch lengths for "
            "collapsed phylogeny."
        )

    if "ancestor_list" in phylogeny_df:
        raise NotImplementedError

    original_ids = phylogeny_df["id"]
    has_contiguous_ids = phylogeny_df.select(
        pl.col("id").diff() == 1
    ).to_series().all() and (phylogeny_df["id"].first() == 0)
    if not has_contiguous_ids:
        logging.info(
            "- alifestd_collapse_unifurcations_polars: assigning ids...",
        )
        phylogeny_df = alifestd_assign_contiguous_ids_polars(phylogeny_df)

    if (
        not phylogeny_df.select(pl.col("ancestor_id") <= pl.col("id"))
        .to_series()
        .all()
    ):
        raise NotImplementedError(
            "polars topological sort not yet implemented"
        )

    logging.info(
        "- alifestd_collapse_unifurcations_polars: calculating reindex...",
    )
    keep_filter, ancestor_ids = _collapse_unifurcations(
        # must copy to remove read-only flag for numba compatibility
        phylogeny_df["ancestor_id"]
        .to_numpy()
        .copy(),
    )

    logging.info(
        "- alifestd_collapse_unifurcations_polars: applying reindex...",
    )
    return phylogeny_df.filter(keep_filter).with_columns(
        id=original_ids.to_numpy()[keep_filter],
        ancestor_id=original_ids.gather(ancestor_ids[keep_filter]),
    )
