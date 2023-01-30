from collections import Counter
import os

import alifedata_phyloinformatics_convert as apc
import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_assign_contiguous_ids,
    alifestd_find_leaf_ids,
    alifestd_has_contiguous_ids,
    alifestd_is_asexual,
    alifestd_make_ancestor_id_col,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-sexual-phylogeny.csv"
        ),
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_alifestd_assign_contiguous_ids(phylogeny_df):
    phylogeny_df_ = phylogeny_df.copy()
    reassigned_df = alifestd_assign_contiguous_ids(phylogeny_df)
    # check for side effects
    assert phylogeny_df.equals(phylogeny_df_)

    assert alifestd_has_contiguous_ids(reassigned_df)

    assert len(phylogeny_df) == len(reassigned_df)
    assert len(alifestd_find_leaf_ids(phylogeny_df)) == len(
        alifestd_find_leaf_ids(reassigned_df)
    )
    if "ancestor_id" in phylogeny_df:
        assert (
            phylogeny_df["ancestor_id"]
            == alifestd_make_ancestor_id_col(
                phylogeny_df["id"],
                phylogeny_df["ancestor_list"],
            )
        ).all()

    if alifestd_is_asexual(phylogeny_df):
        phylogeny_tree = apc.alife_dataframe_to_dendropy_tree(phylogeny_df)
        reassigned_tree = apc.alife_dataframe_to_dendropy_tree(reassigned_df)

        assert Counter(node.level() for node in phylogeny_tree) == Counter(
            node.level() for node in reassigned_tree
        )
        assert Counter(
            len(node.child_nodes()) for node in phylogeny_tree
        ) == Counter(len(node.child_nodes()) for node in reassigned_tree)
        assert Counter(
            (node.level(), len(node.child_nodes())) for node in phylogeny_tree
        ) == Counter(
            (node.level(), len(node.child_nodes())) for node in reassigned_tree
        )
