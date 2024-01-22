import pandas as pd

from ._alifestd_count_leaf_nodes import alifestd_count_leaf_nodes


def alifestd_count_inner_nodes(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> int:
    """Count how many non-leaf nodes are contained in phylogeny."""

    num_leaves = alifestd_count_leaf_nodes(phylogeny_df)
    res = len(phylogeny_df) - num_leaves
    assert res >= 0
    return res
