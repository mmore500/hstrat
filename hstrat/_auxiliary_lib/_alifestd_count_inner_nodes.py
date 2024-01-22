import pandas as pd

from ._alifestd_collapse_unifurcations import alifestd_collapse_unifurcations
from ._alifestd_count_leaf_nodes import alifestd_count_leaf_nodes


def alifestd_count_inner_nodes(
    phylogeny_df: pd.DataFrame,
    collapse_unifurcations: bool = False,
    mutate: bool = False,
) -> int:
    """Count how many non-leaf nodes are contained in phylogeny."""
    if collapse_unifurcations:
        if not mutate:
            phylogeny_df = phylogeny_df.copy()
        phylogeny_df = alifestd_collapse_unifurcations(
            phylogeny_df, mutate=True
        )

    num_leaves = alifestd_count_leaf_nodes(phylogeny_df)
    res = len(phylogeny_df) - num_leaves
    assert res >= 0
    assert res < num_leaves or not collapse_unifurcations
    return res
