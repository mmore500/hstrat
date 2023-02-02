import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_aggregate_phylogenies,
    alifestd_is_topologically_sorted,
    alifestd_parse_ancestor_ids,
    alifestd_topological_sort,
    alifestd_validate,
    swap_rows_and_indices,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
        pd.read_csv(
            f"{assets_path}/example-standard-toy-sexual-phylogeny.csv"
        ),
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_alifestd_topological_sort_empty(phylogeny_df):
    phylogeny_df.sort_values("id", ascending=True, inplace=True)
    phylogeny_df_ = phylogeny_df.copy()

    operand = phylogeny_df.iloc[-1:0, :]
    res = alifestd_topological_sort(operand)
    assert alifestd_validate(res)
    assert alifestd_is_topologically_sorted(res)
    assert len(res) == len(operand)
    # ensure no side effects
    assert phylogeny_df.equals(phylogeny_df_)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
        pd.read_csv(
            f"{assets_path}/example-standard-toy-sexual-phylogeny.csv"
        ),
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_alifestd_topological_sort_singleton(phylogeny_df):
    phylogeny_df.sort_values("id", ascending=True, inplace=True)
    phylogeny_df_ = phylogeny_df.copy()

    operand = phylogeny_df.iloc[0:1, :]
    res = alifestd_topological_sort(operand)
    assert alifestd_validate(res)
    assert alifestd_is_topologically_sorted(res)
    assert len(res) == len(operand)
    # ensure no side effects
    assert phylogeny_df.equals(phylogeny_df_)


def test_alifestd_topological_sort_tworoots():

    phylo1 = pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")
    phylo1.sort_values("id", ascending=True, inplace=True)
    phylo2 = pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv")
    phylo2.sort_values("id", ascending=True, inplace=True)

    operand = alifestd_aggregate_phylogenies(
        [
            phylo1.iloc[0:1, :],
            phylo2.iloc[0:1, :],
        ]
    )
    res = alifestd_topological_sort(operand)
    assert alifestd_validate(res)
    assert alifestd_is_topologically_sorted(res)
    assert len(res) == len(operand)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_alifestd_topological_sort_twolineages(phylogeny_df):

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

    operand = alifestd_aggregate_phylogenies(
        [
            lineage1.iloc[::-1, :],
            lineage2,
        ]
    )
    res = alifestd_topological_sort(operand)
    assert alifestd_validate(res)
    assert alifestd_is_topologically_sorted(res)
    assert len(res) == len(operand)

    operand = alifestd_aggregate_phylogenies(
        [
            lineage1.iloc[::-1, :],
            lineage2,
            lineage1.iloc[::-1, :],
        ]
    )
    res = alifestd_topological_sort(operand)
    assert alifestd_validate(res)
    assert alifestd_is_topologically_sorted(res)
    assert len(res) == len(operand)

    operand = alifestd_aggregate_phylogenies(
        [
            lineage1.iloc[::, :],
            lineage2,
            lineage1.iloc[::, :],
        ]
    )
    res = alifestd_topological_sort(operand)
    assert alifestd_validate(res)
    assert alifestd_is_topologically_sorted(res)
    assert len(res) == len(operand)


def test_alifestd_topologically_sort_twolineages_sexual():
    operand = pd.read_csv(
        f"{assets_path}/example-standard-toy-sexual-phylogeny.csv"
    )
    res = alifestd_topological_sort(operand)
    assert alifestd_validate(res)
    assert alifestd_is_topologically_sorted(res)
    assert len(res) == len(operand)

    operand = operand[::-1]
    res = alifestd_topological_sort(operand)
    assert alifestd_validate(res)
    assert alifestd_is_topologically_sorted(res)
    assert len(res) == len(operand)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
        pd.read_csv(
            f"{assets_path}/example-standard-toy-sexual-phylogeny.csv"
        ),
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_alifestd_topological_sort(phylogeny_df):
    phylogeny_df.sort_values("id", ascending=False, inplace=True)
    phylogeny_df.set_index("id", drop=False, inplace=True)
    phylogeny_df_ = phylogeny_df.copy()

    operand = phylogeny_df
    res = alifestd_topological_sort(operand)
    assert alifestd_validate(res)
    assert alifestd_is_topologically_sorted(res)
    assert len(res) == len(operand)
    # check for side effects
    assert phylogeny_df.equals(phylogeny_df_)

    # reverse dataframe
    phylogeny_df = phylogeny_df.iloc[::-1]
    phylogeny_df_ = phylogeny_df.copy()
    assert alifestd_is_topologically_sorted(phylogeny_df)

    # one-by-one transpositions
    for idx, row in phylogeny_df.sample(min(10, len(phylogeny_df))).iterrows():
        for ancestor_id in alifestd_parse_ancestor_ids(row["ancestor_list"]):
            operand = swap_rows_and_indices(phylogeny_df, idx, ancestor_id)
            res = alifestd_topological_sort(operand)
            assert alifestd_validate(res)
            assert alifestd_is_topologically_sorted(res)
            assert len(res) == len(operand)
            # check for side effects
            assert phylogeny_df.equals(phylogeny_df_)

    # cumulative transpositions in random order
    for idx, row in phylogeny_df.sample(min(10, len(phylogeny_df))).iterrows():
        for ancestor_id in alifestd_parse_ancestor_ids(row["ancestor_list"]):
            assert ancestor_id in phylogeny_df_.index
            phylogeny_df = swap_rows_and_indices(
                phylogeny_df, idx, ancestor_id
            )
            res = alifestd_topological_sort(operand)
            assert alifestd_validate(res)
            assert alifestd_is_topologically_sorted(res)
            assert len(res) == len(operand)
