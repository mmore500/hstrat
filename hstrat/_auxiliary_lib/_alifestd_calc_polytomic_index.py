import pandas as pd

from ._alifestd_count_leaf_nodes import alifestd_count_leaf_nodes
from ._alifestd_count_root_nodes import alifestd_count_root_nodes
from ._alifestd_count_unifurcations import alifestd_count_unifurcations


def alifestd_calc_polytomic_index(phylogeny_df: pd.DataFrame) -> int:
    """Count how many fewer inner nodes are contained in phylogeny than expected
    if strictly bifurcationg.

    Excludes unifurcations from calculation.
    """
    num_leaf_nodes = alifestd_count_leaf_nodes(phylogeny_df)
    num_root_nodes = alifestd_count_root_nodes(phylogeny_df)
    expected_rows_if_bifurcating = max(2 * num_leaf_nodes - num_root_nodes, 0)
    num_unifurcations = alifestd_count_unifurcations(phylogeny_df)
    num_non_unifurcating_rows = len(phylogeny_df) - num_unifurcations
    res = expected_rows_if_bifurcating - num_non_unifurcating_rows
    assert 0 <= res < max(expected_rows_if_bifurcating, 1)
    return res
