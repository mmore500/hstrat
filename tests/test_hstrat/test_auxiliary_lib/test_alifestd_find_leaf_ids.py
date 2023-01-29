import itertools as it
import os
import random

import alifedata_phyloinformatics_convert as apc
import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_find_leaf_ids,
    alifestd_parse_ancestor_ids,
    swap_rows_and_indices,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_alifestd_find_leaf_ids_empty(phylogeny_df):
    assert alifestd_find_leaf_ids(phylogeny_df.iloc[-1:0, :]) == []


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_alifestd_find_leaf_ids_singleton(phylogeny_df):
    phylogeny_df.sort_values("id", ascending=True, inplace=True)

    assert alifestd_find_leaf_ids(phylogeny_df.iloc[0:1, :]) == [
        phylogeny_df.iloc[0].at["id"]
    ]


def test_alifestd_find_leaf_ids_tworoots():

    phylo1 = pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")
    phylo1.sort_values("id", ascending=True, inplace=True)

    phylo2 = pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv")
    phylo2.sort_values("id", ascending=True, inplace=True)
    phylo2["id"] += phylo1["id"].max()

    assert alifestd_find_leaf_ids(
        pd.concat(
            [
                phylo1.iloc[0:1, :],
                phylo2.iloc[0:1, :],
            ]
        )
    ) == [phylo1.iloc[0].at["id"]] + [phylo2.iloc[0].at["id"]]


def _test_alifestd_find_leaf_ids_impl(phylogeny_df):
    phylogeny_df_ = phylogeny_df.set_index("id")
    trees = apc.alife_dataframe_to_dendropy_trees(phylogeny_df)
    leaf_ids = [
        leaf_node.id for tree in trees for leaf_node in tree.leaf_node_iter()
    ]
    leaf_ids.sort(key=phylogeny_df_.index.get_loc)

    assert leaf_ids == alifestd_find_leaf_ids(phylogeny_df)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_alifestd_find_leaf_ids_twolineages(phylogeny_df):

    phylogeny_df.sort_values("id", ascending=True, inplace=True)
    phylogeny_df.reset_index(inplace=True)
    max_id = phylogeny_df["id"].max()

    lineage1 = phylogeny_df.copy()
    lineage2 = phylogeny_df.copy()
    lineage2["id"] += max_id
    lineage2["ancestor_list"] = lineage2["ancestor_list"].apply(
        lambda ancestor_list_str: str(
            [
                ancestor_id + max_id
                for ancestor_id in alifestd_parse_ancestor_ids(
                    ancestor_list_str
                )
            ]
        )
    )
    _test_alifestd_find_leaf_ids_impl(
        pd.concat(
            [
                lineage1,
                lineage2,
            ]
        )
    )
    _test_alifestd_find_leaf_ids_impl(
        pd.concat(
            [
                lineage1,
                lineage2,
            ]
        ).sort_index()
    )

    _test_alifestd_find_leaf_ids_impl(
        pd.concat(
            [
                lineage1.iloc[::-1, :],
                lineage2,
            ]
        )
    )
    _test_alifestd_find_leaf_ids_impl(
        pd.concat(
            [
                lineage1.iloc[:10:-1, :],
                lineage2,
                lineage1.iloc[10::-1, :],
            ]
        )
    )
    _test_alifestd_find_leaf_ids_impl(
        pd.concat(
            [
                lineage1.iloc[10::, :],
                lineage2,
                lineage1.iloc[:10:, :],
            ]
        )
    )


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_alifestd_find_leaf_ids_true(phylogeny_df):
    phylogeny_df.sort_values("id", ascending=True, inplace=True)

    phylogeny_df_ = phylogeny_df.copy()
    _test_alifestd_find_leaf_ids_impl(phylogeny_df)

    # check for side effects
    assert phylogeny_df.equals(phylogeny_df_)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_alifestd_find_leaf_ids_false(phylogeny_df):
    phylogeny_df.sort_values("id", ascending=True, inplace=True)
    phylogeny_df_ = phylogeny_df.copy()
    _test_alifestd_find_leaf_ids_impl(phylogeny_df)
    # check for side effects
    assert phylogeny_df.equals(phylogeny_df_)

    phylogeny_df.sort_values("id", ascending=False, inplace=True)
    phylogeny_df.set_index("id", drop=False, inplace=True)

    phylogeny_df_ = phylogeny_df.copy()
    _test_alifestd_find_leaf_ids_impl(phylogeny_df)
    # check for side effects
    assert phylogeny_df.equals(phylogeny_df_)

    # one-by-one transpositions
    for idx, row in phylogeny_df.sample(10).iterrows():
        for ancestor_id in alifestd_parse_ancestor_ids(row["ancestor_list"]):
            phylogeny_df_ = swap_rows_and_indices(
                phylogeny_df, idx, ancestor_id
            )
            _test_alifestd_find_leaf_ids_impl(phylogeny_df_)

    # cumulative transpositions in random order
    for idx, row in phylogeny_df.sample(10).iterrows():
        for ancestor_id in alifestd_parse_ancestor_ids(row["ancestor_list"]):
            assert ancestor_id in phylogeny_df_.index
            phylogeny_df = swap_rows_and_indices(
                phylogeny_df, idx, ancestor_id
            )
            _test_alifestd_find_leaf_ids_impl(phylogeny_df)