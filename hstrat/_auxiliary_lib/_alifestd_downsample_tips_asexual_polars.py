import logging
import typing

import numpy as np
import polars as pl

from ._alifestd_mark_leaves_asexual_polars import (
    alifestd_mark_leaves_asexual_polars,
)
from ._alifestd_prune_extinct_lineages_asexual_polars import (
    alifestd_prune_extinct_lineages_asexual_polars,
)
from ._with_rng_state_context import with_rng_state_context


def _alifestd_downsample_tips_asexual_polars_impl(
    phylogeny_df: pl.DataFrame,
    n_downsample: int,
) -> pl.DataFrame:
    """Implementation detail for alifestd_downsample_tips_asexual_polars."""
    logging.info(
        "- alifestd_downsample_tips_asexual_polars: finding leaf ids...",
    )
    marked_df = alifestd_mark_leaves_asexual_polars(phylogeny_df)
    tips = np.flatnonzero(marked_df["is_leaf"].to_numpy())

    logging.info(
        "- alifestd_downsample_tips_asexual_polars: sampling tips...",
    )
    kept = np.random.choice(tips, min(n_downsample, len(tips)), replace=False)

    extant = np.zeros(len(phylogeny_df), dtype=bool)
    extant[kept] = True

    phylogeny_df = phylogeny_df.with_columns(
        extant=pl.Series(extant),
    )

    logging.info(
        "- alifestd_downsample_tips_asexual_polars: pruning...",
    )
    return alifestd_prune_extinct_lineages_asexual_polars(
        phylogeny_df,
    ).drop("extant")


def alifestd_downsample_tips_asexual_polars(
    phylogeny_df: pl.DataFrame,
    n_downsample: int,
    seed: typing.Optional[int] = None,
) -> pl.DataFrame:
    """Create a subsample phylogeny containing `n_downsample` tips.

    If `n_downsample` is greater than the number of tips in the phylogeny,
    the whole phylogeny is returned.

    Only supports asexual phylogenies.

    Parameters
    ----------
    phylogeny_df : polars.DataFrame
        The phylogeny as a dataframe in alife standard format.

        Must represent an asexual phylogeny.
    n_downsample : int
        Number of tips to retain.
    seed : int, optional
        Integer seed for deterministic behavior.

    Raises
    ------
    NotImplementedError
        If `phylogeny_df` has no "ancestor_id" column.
    NotImplementedError
        If `phylogeny_df` has non-contiguous ids.
    NotImplementedError
        If `phylogeny_df` is not topologically sorted.

    Returns
    -------
    polars.DataFrame
        The downsampled phylogeny in alife standard format.
    """
    if "ancestor_id" not in phylogeny_df.columns:
        raise NotImplementedError(
            "ancestor_id column required; ancestor_list not supported"
        )

    if phylogeny_df.is_empty():
        return phylogeny_df

    impl = (
        with_rng_state_context(seed)(
            _alifestd_downsample_tips_asexual_polars_impl
        )
        if seed is not None
        else _alifestd_downsample_tips_asexual_polars_impl
    )

    return impl(phylogeny_df, n_downsample)
