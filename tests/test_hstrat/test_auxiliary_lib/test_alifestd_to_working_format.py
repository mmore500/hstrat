from collections import Counter
import os

import alifedata_phyloinformatics_convert as apc
import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_aggregate_phylogenies,
    alifestd_find_leaf_ids,
    alifestd_has_contiguous_ids,
    alifestd_is_asexual,
    alifestd_is_topologically_sorted,
    alifestd_parse_ancestor_ids,
    alifestd_to_working_format,
    alifestd_validate,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-sexual-phylogeny.csv"
        ),
        alifestd_aggregate_phylogenies(
            [
                pd.read_csv(
                    f"{assets_path}/example-standard-toy-sexual-phylogeny.csv"
                ),
                pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
            ]
        ),
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        alifestd_aggregate_phylogenies(
            [
                pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
                pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
            ]
        ),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_alifestd_to_working_format(phylogeny_df):
    phylogeny_df_ = phylogeny_df.copy()
    working_df = alifestd_to_working_format(phylogeny_df)
    assert alifestd_validate(working_df)
    # check for side effects
    assert phylogeny_df.equals(phylogeny_df_)

    assert alifestd_has_contiguous_ids(working_df)
    assert alifestd_is_topologically_sorted(working_df)

    assert len(phylogeny_df) == len(working_df)
    assert len(alifestd_find_leaf_ids(phylogeny_df)) == len(
        alifestd_find_leaf_ids(working_df)
    )

    if alifestd_is_asexual(phylogeny_df):
        phylogeny_trees = apc.alife_dataframe_to_dendropy_trees(phylogeny_df)
        working_trees = apc.alife_dataframe_to_dendropy_trees(working_df)

        assert Counter(
            node.level() for tree in phylogeny_trees for node in tree
        ) == Counter(node.level() for tree in working_trees for node in tree)
        assert Counter(
            len(node.child_nodes())
            for tree in phylogeny_trees
            for node in tree
        ) == Counter(
            len(node.child_nodes()) for tree in working_trees for node in tree
        )
        assert Counter(
            (node.level(), len(node.child_nodes()))
            for tree in phylogeny_trees
            for node in tree
        ) == Counter(
            (node.level(), len(node.child_nodes()))
            for tree in working_trees
            for node in tree
        )

        assert "ancestor_id" in working_df
        assert set(
            working_df.loc[
                working_df["ancestor_id"] != working_df["id"],
                "ancestor_id",
            ]
        ) == set(
            ancestor_id
            for ancestor_list_str in working_df["ancestor_list"]
            for ancestor_id in alifestd_parse_ancestor_ids(ancestor_list_str)
        )
