from collections import Counter, defaultdict
import itertools as it
import os
import typing

import pandas as pd
import pandas.testing as pdt
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_aggregate_phylogenies,
    alifestd_assign_contiguous_ids,
    alifestd_collapse_unifurcations,
    alifestd_collapse_unifurcations_polars,
    alifestd_count_root_nodes,
    alifestd_find_leaf_ids,
    alifestd_find_mrca_id_asexual,
    alifestd_find_root_ids,
    alifestd_is_asexual,
    alifestd_is_sexual,
    alifestd_is_topologically_sorted,
    alifestd_parse_ancestor_ids,
    alifestd_test_leaves_isomorphic_asexual,
    alifestd_to_working_format,
    alifestd_topological_sort,
    alifestd_try_add_ancestor_id_col,
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
@pytest.mark.parametrize(
    "apply",
    [
        alifestd_assign_contiguous_ids,
        alifestd_to_working_format,
        alifestd_topological_sort,
        alifestd_try_add_ancestor_id_col,
        lambda x: x,
    ],
)
@pytest.mark.parametrize(
    "root_ancestor_token",
    [
        "",
        "None",
        "none",
    ],
)
def test_alifestd_collapse_unifurcations(
    phylogeny_df: pd.DataFrame,
    apply: typing.Callable,
    root_ancestor_token: str,
):
    phylogeny_df = apply(phylogeny_df.copy())

    phylogeny_df_ = phylogeny_df.copy()
    collapsed_df = alifestd_collapse_unifurcations(
        phylogeny_df, root_ancestor_token=root_ancestor_token
    )
    assert len(alifestd_find_root_ids(phylogeny_df)) == sum(
        collapsed_df["ancestor_list"] == f"[{root_ancestor_token}]"
    )
    assert alifestd_validate(collapsed_df)
    assert phylogeny_df.equals(phylogeny_df_)

    assert alifestd_is_asexual(collapsed_df) == alifestd_is_asexual(
        phylogeny_df
    )
    assert alifestd_is_sexual(collapsed_df) == alifestd_is_sexual(phylogeny_df)
    if alifestd_is_asexual(phylogeny_df):
        assert len(collapsed_df) <= len(phylogeny_df)

    assert set(alifestd_find_leaf_ids(phylogeny_df)) == set(
        alifestd_find_leaf_ids(collapsed_df)
    )

    if alifestd_is_asexual(phylogeny_df):
        pdt.assert_frame_equal(
            collapsed_df.drop(
                "ancestor_list", axis=1, errors="ignore"
            ).reset_index(drop=True),
            alifestd_collapse_unifurcations_polars(
                pl.from_pandas(
                    alifestd_try_add_ancestor_id_col(collapsed_df).drop(
                        "ancestor_list", axis=1, errors="ignore"
                    )
                )
            ).to_pandas(),
            check_dtype=False,
        )

    phylogeny_df_ = phylogeny_df.set_index("id", drop=False)
    for _idx, row in collapsed_df.iterrows():
        assert all(
            phylogeny_df_.loc[row["id"]]
            .drop(["ancestor_list", "ancestor_id"], errors="ignore")
            .dropna()
            == row.drop(
                ["ancestor_list", "ancestor_id"], errors="ignore"
            ).dropna()
        )

    ref_counts = Counter(
        id_
        for ancestor_list_str in collapsed_df["ancestor_list"]
        for id_ in alifestd_parse_ancestor_ids(ancestor_list_str)
    )
    for _idx, row in collapsed_df.iterrows():
        if len(alifestd_parse_ancestor_ids(row["ancestor_list"])) == 1:
            assert ref_counts[row["id"]] != 1

    phylogeny_df = alifestd_topological_sort(phylogeny_df)
    assert alifestd_is_topologically_sorted(collapsed_df)

    collapsed_descendants_lookup = defaultdict(set)
    phylogeny_descendants_lookup = defaultdict(set)

    for df, lookup in (
        (phylogeny_df, phylogeny_descendants_lookup),
        (collapsed_df, collapsed_descendants_lookup),
    ):
        for _idx, row in df[::-1].iterrows():
            id_ = row["id"]
            ancestor_ids = alifestd_parse_ancestor_ids(row["ancestor_list"])
            lookup[id_].add(id_)
            for ancestor_id in ancestor_ids:
                lookup[ancestor_id] |= lookup[id_]

    dropped_ids = set(phylogeny_df["id"]) - set(collapsed_df["id"])
    for id_, descendants in collapsed_descendants_lookup.items():
        assert descendants <= phylogeny_descendants_lookup[id_]
        assert descendants == (phylogeny_descendants_lookup[id_] - dropped_ids)


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_collapse_unifurcations_collapse1(mutate: bool):
    # 0 -> 1 -> 2 -> 4
    #        -> 3
    # 5
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 4, 3, 5],
            "ancestor_id": [0, 0, 1, 2, 1, 5],
            "taxon_label": ["0", "1", "2", "4", "3", "5"],
        },
    )
    original_df = df.copy()
    result = alifestd_collapse_unifurcations(df)
    print(result)

    expected = pd.DataFrame(
        {
            "id": [0, 1, 4, 3, 5],
            "ancestor_id": [0, 0, 1, 1, 5],
            "taxon_label": ["0", "1", "4", "3", "5"],
        },
    )
    pd.testing.assert_frame_equal(
        result[expected.columns].reset_index(drop=True),
        expected.reset_index(drop=True),
    )

    if not mutate:
        assert df.equals(original_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_collapse_unifurcations_collapse2(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_id": [0, 0, 1, 0, 0, 2, 3],
        },
    )
    original_df = df.copy()
    result = alifestd_collapse_unifurcations(df)

    expected = pd.DataFrame(
        {
            "id": [0, 4, 5, 6],
            "ancestor_id": [0, 0, 0, 0],
        },
    )
    pd.testing.assert_frame_equal(
        result[expected.columns].reset_index(drop=True),
        expected.reset_index(drop=True),
    )

    if not mutate:
        assert df.equals(original_df)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(f"{assets_path}/trunktestphylo.csv"),
    ],
)
@pytest.mark.parametrize(
    "apply",
    [
        alifestd_assign_contiguous_ids,
        alifestd_to_working_format,
        alifestd_topological_sort,
        lambda x: x.sample(frac=1),
        lambda x: x,
    ],
)
def test_alifestd_collapse_unifurcations_trunktest(
    phylogeny_df: pd.DataFrame, apply: typing.Callable
):
    phylogeny_df = apply(phylogeny_df.copy())

    phylogeny_df_ = phylogeny_df.copy()
    collapsed_df = alifestd_collapse_unifurcations(phylogeny_df)
    assert alifestd_count_root_nodes(
        phylogeny_df
    ) == alifestd_count_root_nodes(
        collapsed_df,
    )
    assert phylogeny_df.equals(phylogeny_df_)

    assert alifestd_is_asexual(collapsed_df) == alifestd_is_asexual(
        phylogeny_df
    )
    # assert len(collapsed_df) < len(phylogeny_df)

    assert alifestd_count_root_nodes(
        collapsed_df
    ) == alifestd_count_root_nodes(phylogeny_df)

    original_leaf_ids = alifestd_find_leaf_ids(phylogeny_df)
    collapsed_leaf_ids = alifestd_find_leaf_ids(collapsed_df)
    assert len(original_leaf_ids) == len(collapsed_leaf_ids)
    assert set(original_leaf_ids) == set(collapsed_leaf_ids)

    for first, second in it.combinations(original_leaf_ids, 2):
        assert alifestd_find_mrca_id_asexual(
            collapsed_df, [first, second]
        ) == alifestd_find_mrca_id_asexual(phylogeny_df, [first, second])

    assert alifestd_test_leaves_isomorphic_asexual(
        collapsed_df, phylogeny_df, taxon_label="id"
    )
