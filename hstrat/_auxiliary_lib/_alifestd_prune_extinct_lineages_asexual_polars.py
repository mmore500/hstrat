import logging

import numpy as np
import polars as pl

from ._alifestd_prune_extinct_lineages_asexual import (
    _create_has_extant_descendant_contiguous_sorted,
)


def alifestd_prune_extinct_lineages_asexual_polars(
    phylogeny_df: pl.DataFrame,
) -> pl.DataFrame:
    """Drop taxa without extant descendants.

    An "extant" column, if provided, is used to determine extant taxa.
    Otherwise, taxa with inf or nan "destruction_time" are considered extant.

    Parameters
    ----------
    phylogeny_df : polars.DataFrame
        The phylogeny as a dataframe in alife standard format.

        Must represent an asexual phylogeny.

    Raises
    ------
    NotImplementedError
        If `phylogeny_df` has no "ancestor_id" column.
    NotImplementedError
        If `phylogeny_df` has non-contiguous ids.
    NotImplementedError
        If `phylogeny_df` is not topologically sorted.
    ValueError
        If `phylogeny_df` has neither "extant" or "destruction_time" columns.

    Returns
    -------
    polars.DataFrame
        The pruned phylogeny in alife standard format.
    """
    if "ancestor_id" not in phylogeny_df.columns:
        raise NotImplementedError(
            "ancestor_id column required; ancestor_list not supported"
        )

    logging.info(
        "- alifestd_prune_extinct_lineages_asexual_polars: "
        "checking contiguous ids...",
    )
    has_contiguous_ids = phylogeny_df.select(
        pl.col("id").diff() == 1
    ).to_series().all() and (phylogeny_df["id"].first() == 0)
    if not has_contiguous_ids:
        raise NotImplementedError("non-contiguous ids not yet supported")

    logging.info(
        "- alifestd_prune_extinct_lineages_asexual_polars: "
        "checking topological sort...",
    )
    if (
        not phylogeny_df.select(pl.col("ancestor_id") <= pl.col("id"))
        .to_series()
        .all()
    ):
        raise NotImplementedError(
            "polars topological sort not yet implemented"
        )

    logging.info(
        "- alifestd_prune_extinct_lineages_asexual_polars: "
        "determining extant mask...",
    )
    if "extant" in phylogeny_df.columns:
        extant_mask = phylogeny_df["extant"].to_numpy().astype(bool)
    elif "destruction_time" in phylogeny_df.columns:
        destruction_time = phylogeny_df["destruction_time"]
        extant_mask = (
            destruction_time.is_nan() | destruction_time.is_infinite()
        ).to_numpy()
    else:
        raise ValueError('Need "extant" or "destruction_time" column.')

    logging.info(
        "- alifestd_prune_extinct_lineages_asexual_polars: "
        "calculating has_extant_descendant...",
    )
    # must copy to remove read-only flag for numba compatibility
    ancestor_ids = (
        phylogeny_df["ancestor_id"].to_numpy().astype(np.uint64).copy()
    )
    has_extant_descendant = _create_has_extant_descendant_contiguous_sorted(
        ancestor_ids,
        extant_mask.copy(),
    )

    logging.info(
        "- alifestd_prune_extinct_lineages_asexual_polars: filtering...",
    )
    return phylogeny_df.filter(pl.Series(has_extant_descendant))
