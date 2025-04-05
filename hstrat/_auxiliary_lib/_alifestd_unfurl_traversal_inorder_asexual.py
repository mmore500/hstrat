import numpy as np
import pandas as pd

from ._alifestd_find_leaf_ids import alifestd_find_leaf_ids
from ._alifestd_has_multiple_roots import alifestd_has_multiple_roots
from ._alifestd_is_strictly_bifurcating_asexual import (
    alifestd_is_strictly_bifurcating_asexual,
)
from ._alifestd_is_working_format_asexual import (
    alifestd_is_working_format_asexual,
)
from ._alifestd_mark_leaves import alifestd_mark_leaves
from ._alifestd_mark_num_descendants_asexual import (
    alifestd_mark_num_descendants_asexual,
)
from ._alifestd_mark_num_preceding_leaves_asexual import (
    alifestd_mark_num_preceding_leaves_asexual,
)
from ._alifestd_unfurl_traversal_semiorder_asexual import (
    _alifestd_unfurl_traversal_semiorder_asexual_fast_path,
    _alifestd_unfurl_traversal_semiorder_asexual_slow_path,
)


def alifestd_unfurl_traversal_inorder_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> np.ndarray:
    """List `id` values in semiorder traversal order, with left children
    visited first.

    The provided dataframe must be asexual and strictly bifurcating.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if alifestd_has_multiple_roots(phylogeny_df):
        raise ValueError(
            "Phylogeny must have a single root for inorder traversal."
        )
    if not alifestd_is_strictly_bifurcating_asexual(phylogeny_df):
        raise ValueError(
            "Phylogeny must be strictly bifurcating for inorder traversal.",
        )

    if "num_preceding_leaves" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_num_preceding_leaves_asexual(
            phylogeny_df,
            mutate=True,
        )

    if alifestd_is_working_format_asexual(phylogeny_df, mutate=True):
        if "num_descendants" not in phylogeny_df.columns:
            phylogeny_df = alifestd_mark_num_descendants_asexual(
                phylogeny_df, mutate=True
            )
        leaf_positions = phylogeny_df["num_preceding_leaves"].to_numpy()

        leaf_ids = alifestd_find_leaf_ids(phylogeny_df)
        sorted_leaf_ids = np.empty_like(leaf_ids)
        sorted_leaf_ids[leaf_positions[leaf_ids]] = leaf_ids

        return _alifestd_unfurl_traversal_semiorder_asexual_fast_path(
            phylogeny_df["ancestor_id"].to_numpy(),
            phylogeny_df["num_descendants"].to_numpy(),
            sorted_leaf_ids,
        )
    else:
        if "is_leaf" not in phylogeny_df.columns:
            phylogeny_df = alifestd_mark_leaves(phylogeny_df, mutate=True)

        sorted_phylogeny_df = phylogeny_df.sort_values("num_preceding_leaves")
        sorted_leaf_ids = sorted_phylogeny_df.loc[
            sorted_phylogeny_df["is_leaf"], "id"
        ]

        return _alifestd_unfurl_traversal_semiorder_asexual_slow_path(
            phylogeny_df,
            sorted_leaf_ids,
        )
