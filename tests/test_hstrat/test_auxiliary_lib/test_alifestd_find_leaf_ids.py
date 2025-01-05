import os

import alifedata_phyloinformatics_convert as apc
import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_aggregate_phylogenies,
    alifestd_find_leaf_ids,
    alifestd_is_asexual,
    alifestd_parse_ancestor_ids,
    alifestd_to_working_format,
    alifestd_try_add_ancestor_id_col,
    swap_rows_and_indices,
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
@pytest.mark.parametrize(
    "apply",
    [
        alifestd_to_working_format,
        alifestd_try_add_ancestor_id_col,
        lambda x: x,
    ],
)
def test_alifestd_find_leaf_ids_empty(phylogeny_df, apply):
    phylogeny_df = phylogeny_df.copy()
    phylogeny_df = apply(phylogeny_df)
    assert alifestd_find_leaf_ids(phylogeny_df.iloc[-1:0, :]).tolist() == []


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
@pytest.mark.parametrize(
    "apply",
    [
        alifestd_to_working_format,
        alifestd_try_add_ancestor_id_col,
        lambda x: x,
    ],
)
def test_alifestd_find_leaf_ids_singleton(phylogeny_df, apply):
    phylogeny_df = phylogeny_df.copy()
    phylogeny_df = apply(phylogeny_df)
    phylogeny_df.sort_values("id", ascending=True, inplace=True)

    assert alifestd_find_leaf_ids(phylogeny_df.iloc[0:1, :]).tolist() == [
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
    ).tolist() == [phylo1.iloc[0].at["id"]] + [phylo2.iloc[0].at["id"]]


def test_alifestd_find_leaf_ids_empty2():
    phylo1 = pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")
    assert alifestd_find_leaf_ids(phylo1[-1:0]).tolist() == []
    phylo1["ancestor_id"] = 0
    assert alifestd_find_leaf_ids(phylo1[-1:0]).tolist() == []


def _test_alifestd_find_leaf_ids_impl(phylogeny_df):
    phylogeny_df_ = phylogeny_df.set_index("id")
    if alifestd_is_asexual(phylogeny_df):
        trees = apc.alife_dataframe_to_dendropy_trees(phylogeny_df)
        leaf_ids = [
            leaf_node.id
            for tree in trees
            for leaf_node in tree.leaf_node_iter()
        ]
        leaf_ids.sort(key=phylogeny_df_.index.get_loc)

        assert leaf_ids == alifestd_find_leaf_ids(phylogeny_df).tolist()
    else:
        # sexual phylogenies
        leaf_ids = alifestd_find_leaf_ids(phylogeny_df).tolist()
        assert sorted(leaf_ids, key=phylogeny_df_.index.get_loc) == leaf_ids

        all_ids = set(phylogeny_df["id"])
        internal_ids = all_ids - set(leaf_ids)

        for leaf_id in leaf_ids:
            assert not any(
                leaf_id in alifestd_parse_ancestor_ids(ancestor_list_str)
                for ancestor_list_str in phylogeny_df["ancestor_list"]
            )
        for internal_id in internal_ids:
            assert any(
                internal_id in alifestd_parse_ancestor_ids(ancestor_list_str)
                for ancestor_list_str in phylogeny_df["ancestor_list"]
            )


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
@pytest.mark.parametrize(
    "apply",
    [
        alifestd_to_working_format,
        alifestd_try_add_ancestor_id_col,
        lambda x: x,
    ],
)
def test_alifestd_find_leaf_ids_twolineages(phylogeny_df, apply):
    phylogeny_df = phylogeny_df.copy()
    phylogeny_df = apply(phylogeny_df)

    phylogeny_df.sort_values("id", ascending=True, inplace=True)
    phylogeny_df.reset_index(inplace=True)

    aggregated_df = alifestd_aggregate_phylogenies(
        [
            phylogeny_df.copy(),
            phylogeny_df.copy(),
        ]
    )

    lineage1 = aggregated_df[len(phylogeny_df) :]
    lineage2 = aggregated_df[: len(phylogeny_df)]

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
@pytest.mark.parametrize(
    "apply",
    [
        alifestd_to_working_format,
        alifestd_try_add_ancestor_id_col,
        lambda x: x,
    ],
)
def test_alifestd_find_leaf_ids_true(phylogeny_df, apply):
    phylogeny_df = phylogeny_df.copy()
    phylogeny_df = apply(phylogeny_df)

    phylogeny_df.sort_values("id", ascending=True, inplace=True)

    phylogeny_df_ = phylogeny_df.copy()
    _test_alifestd_find_leaf_ids_impl(phylogeny_df)

    # check for side effects
    assert phylogeny_df.equals(phylogeny_df_)


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
@pytest.mark.parametrize(
    "apply",
    [
        alifestd_to_working_format,
        alifestd_try_add_ancestor_id_col,
        lambda x: x,
    ],
)
def test_alifestd_find_leaf_ids_false(phylogeny_df, apply):
    phylogeny_df = phylogeny_df.copy()
    phylogeny_df = apply(phylogeny_df)

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
    for idx, row in phylogeny_df.sample(min(10, len(phylogeny_df))).iterrows():
        for ancestor_id in alifestd_parse_ancestor_ids(row["ancestor_list"]):
            phylogeny_df_ = swap_rows_and_indices(
                phylogeny_df, idx, ancestor_id
            )
            _test_alifestd_find_leaf_ids_impl(phylogeny_df_)

    # cumulative transpositions in random order
    for idx, row in phylogeny_df.sample(min(10, len(phylogeny_df))).iterrows():
        for ancestor_id in alifestd_parse_ancestor_ids(row["ancestor_list"]):
            assert ancestor_id in phylogeny_df_.index
            phylogeny_df = swap_rows_and_indices(
                phylogeny_df, idx, ancestor_id
            )
            _test_alifestd_find_leaf_ids_impl(phylogeny_df)
