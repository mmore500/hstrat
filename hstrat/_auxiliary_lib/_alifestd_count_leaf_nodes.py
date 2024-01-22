import pandas as pd

from ._alifestd_find_leaf_ids import alifestd_find_leaf_ids


def alifestd_count_leaf_nodes(phylogeny_df: pd.DataFrame) -> int:
    """How many leaf nodes are contained in phylogeny?"""
    return len(alifestd_find_leaf_ids(phylogeny_df))
