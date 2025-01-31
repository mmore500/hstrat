import pandas as pd

from ._alifestd_collapse_unifurcations import alifestd_collapse_unifurcations
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_mark_leaves import alifestd_mark_leaves
from ._alifestd_to_working_format import alifestd_to_working_format


def alifestd_test_leaves_isomorphic_asexual(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    taxon_label: str,
    mutate: bool = False,
) -> bool:
    """Test if phylogenetic relationships between leaf nodes are topologically
    isomorphic."""

    if taxon_label == "id":
        raise ValueError("taxon_label must not be 'id'")

    if not mutate:
        df1, df2 = df1.copy(), df2.copy()

    df1 = alifestd_to_working_format(df1, mutate=True)
    df2 = alifestd_to_working_format(df2, mutate=True)

    df1 = alifestd_collapse_unifurcations(df1, mutate=True)
    df2 = alifestd_collapse_unifurcations(df2, mutate=True)

    df1 = alifestd_to_working_format(df1, mutate=True)
    df2 = alifestd_to_working_format(df2, mutate=True)

    df1 = alifestd_mark_leaves(df1, mutate=True)
    df2 = alifestd_mark_leaves(df2, mutate=True)

    df1, df2 = df1.reset_index(drop=True), df2.reset_index(drop=True)
    assert alifestd_has_contiguous_ids(df1)
    assert alifestd_has_contiguous_ids(df2)

    if len(df1) != len(df2):
        return False

    leaves1, leaves2 = df1[df1["is_leaf"]], df2[df2["is_leaf"]]

    if set(leaves1[taxon_label]) != set(leaves2[taxon_label]):
        return False

    df2_id_lookup = dict(zip(leaves2[taxon_label], leaves2["id"]))
    id_map = dict(zip(leaves1["id"], leaves1[taxon_label].map(df2_id_lookup)))

    for id1 in df1["id"][::-1]:
        assert id1 in id_map
        ancestor_id1 = df1["ancestor_id"].iat[id1]

        id2 = id_map[id1]
        ancestor_id2 = df2["ancestor_id"].iat[id2]

        if ancestor_id1 in id_map:
            if id_map[ancestor_id1] != ancestor_id2:
                return False
        else:
            id_map[ancestor_id1] = ancestor_id2

    return True
