import os
import typing

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_calc_clade_trait_count_asexual,
    alifestd_make_empty,
    alifestd_mark_leaves,
    alifestd_mark_num_leaves_asexual,
    alifestd_to_working_format,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def test_empty():
    phylogeny_df = alifestd_make_empty()
    phylogeny_df["origin_time"] = None
    res = alifestd_calc_clade_trait_count_asexual(
        phylogeny_df,
        trait_mask=[],
    )
    assert len(res) == 0


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple1(apply: typing.Callable, mutate: bool):
    # Chain tree: 0 -> 1 -> 2
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result = alifestd_calc_clade_trait_count_asexual(
        phylogeny_df,
        mutate=mutate,
        trait_mask=[False, True, True],
    )
    assert result[0] == 2
    assert result[1] == 2
    assert result[2] == 1

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple2(mutate: bool):
    # Tree structure:
    #        |---- 4
    #   |--- 0 --- 3
    #   1
    #   |--- 2
    phylogeny_df = pd.DataFrame(
        {
            "id": [3, 0, 1, 2, 4],
            "ancestor_list": ["[0]", "[1]", "[None]", "[1]", "[0]"],
            "origin_time": [50, 20, 10, 30, 40],
        },
    )
    original_df = phylogeny_df.copy()
    result = alifestd_calc_clade_trait_count_asexual(
        phylogeny_df,
        mutate=mutate,
        trait_mask=[False, True, True, False, True],
    )
    assert result[0] == 0
    assert result[1] == 2
    assert result[2] == 3
    assert result[3] == 0
    assert result[4] == 1

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple4(apply: typing.Callable, mutate: bool):
    # Tree structure:
    #         0
    #       /   \
    #      1     2
    #     / \   / \
    #    3   4 5   6
    #
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_list": [
                "[None]",
                "[0]",
                "[0]",
                "[1]",
                "[1]",
                "[2]",
                "[2]",
            ],
            "origin_time": [0, 10, 20, 40, 30, 50, 60],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result = alifestd_calc_clade_trait_count_asexual(
        phylogeny_df,
        mutate=mutate,
        trait_mask=[False, True, True, False, True, False, False],
    )
    assert result[0] == 3
    assert result[1] == 2
    assert result[2] == 1
    assert result[3] == 0
    assert result[4] == 1
    assert result[5] == 0
    assert result[6] == 0

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple5(apply: typing.Callable, mutate: bool):
    # Tree structure:
    #         0             7
    #       /   \          / \
    #      1     2        8   9
    #     / \
    #    3   4
    #       / \
    #      5   6
    #
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            "ancestor_list": [
                "[None]",
                "[0]",
                "[0]",
                "[1]",
                "[1]",
                "[4]",
                "[4]",
                "[None]",
                "[7]",
                "[7]",
            ],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result = alifestd_calc_clade_trait_count_asexual(
        phylogeny_df,
        mutate=mutate,
        trait_mask=[
            False,
            True,
            True,
            False,
            True,
            False,
            False,
            True,
            False,
            False,
        ],
    )
    assert result[0] == 3
    assert result[1] == 2
    assert result[2] == 1
    assert result[3] == 0
    assert result[4] == 1
    assert result[5] == 0
    assert result[6] == 0
    assert result[7] == 1
    assert result[8] == 0
    assert result[9] == 0

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_fuzz(phylogeny_df: pd.DataFrame):
    phylogeny_df = alifestd_mark_leaves(phylogeny_df)
    phylogeny_df = alifestd_mark_num_leaves_asexual(phylogeny_df)
    original = phylogeny_df.copy()

    result = alifestd_calc_clade_trait_count_asexual(
        phylogeny_df, trait_mask=phylogeny_df["is_leaf"]
    )
    assert (result == phylogeny_df["num_leaves"]).all()

    # Confirm that the input dataframe is not mutated.
    assert original.equals(phylogeny_df)
