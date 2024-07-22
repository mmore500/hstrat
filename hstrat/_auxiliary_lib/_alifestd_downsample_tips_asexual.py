import random
import typing

import pandas as pd

from ._alifestd_find_leaf_ids import alifestd_find_leaf_ids
from ._alifestd_prune_extinct_lineages_asexual import (
    alifestd_prune_extinct_lineages_asexual,
)
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._with_rng_state_context import with_rng_state_context


def _alifestd_downsample_tips_asexual_impl(
    phylogeny_df: pd.DataFrame,
    n_downsample: int,
) -> pd.DataFrame:
    """Implementation detail for alifestd_downsample_tips_asexual."""
    tips = alifestd_find_leaf_ids(phylogeny_df)
    kept = random.sample(tips, min(n_downsample, len(tips)))
    phylogeny_df["extant"] = phylogeny_df["id"].isin(kept)

    return alifestd_prune_extinct_lineages_asexual(
        phylogeny_df, mutate=True
    ).drop(columns=["extant"])


def alifestd_downsample_tips_asexual(
    phylogeny_df: pd.DataFrame,
    n_downsample: int,
    mutate: bool = False,
    seed: typing.Optional[int] = None,
) -> pd.DataFrame:
    """Subsample phylogeny containing `num_tips` tips. If `num_tips` is greater
    than the number of tips in the phylogeny, the whole phylogeny is returned.

    Only supports asexual phylogenies.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df)
    if "ancestor_id" not in phylogeny_df.columns:
        raise ValueError(
            "alifestd_downsample_tips_asexual only supports "
            "asexual phylogenies.",
        )

    if phylogeny_df.empty:
        return phylogeny_df

    impl = (
        with_rng_state_context(seed)(_alifestd_downsample_tips_asexual_impl)
        if seed is not None
        else _alifestd_downsample_tips_asexual_impl
    )

    return impl(phylogeny_df, n_downsample)
