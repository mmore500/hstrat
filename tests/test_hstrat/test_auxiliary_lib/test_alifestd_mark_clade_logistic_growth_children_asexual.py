import math
import os
import typing

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_collapse_unifurcations,
    alifestd_delete_unifurcating_roots_asexual,
    alifestd_make_empty,
    alifestd_mark_clade_logistic_growth_children_asexual,
    alifestd_mark_leaves,
    alifestd_splay_polytomies,
    alifestd_to_working_format,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def test_empty():
    phylogeny_df = alifestd_make_empty()
    phylogeny_df["origin_time"] = None
    res = alifestd_mark_clade_logistic_growth_children_asexual(
        phylogeny_df,
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
    with pytest.raises(ValueError):
        alifestd_mark_clade_logistic_growth_children_asexual(
            phylogeny_df,
            mutate=mutate,
        )

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
    result_df = alifestd_mark_clade_logistic_growth_children_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert math.isnan(result_df.loc[3, "clade_logistic_growth_children"])
    assert result_df.loc[0, "clade_logistic_growth_children"] < 0
    assert result_df.loc[1, "clade_logistic_growth_children"] < 0
    assert math.isnan(result_df.loc[2, "clade_logistic_growth_children"])
    assert math.isnan(result_df.loc[4, "clade_logistic_growth_children"])

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
    result_df = alifestd_mark_clade_logistic_growth_children_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[0, "clade_logistic_growth_children"] > 0
    assert result_df.loc[1, "clade_logistic_growth_children"] < 0
    assert result_df.loc[2, "clade_logistic_growth_children"] > 0
    assert math.isnan(result_df.loc[3, "clade_logistic_growth_children"])
    assert math.isnan(result_df.loc[4, "clade_logistic_growth_children"])
    assert math.isnan(result_df.loc[5, "clade_logistic_growth_children"])
    assert math.isnan(result_df.loc[6, "clade_logistic_growth_children"])

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple5(apply: typing.Callable, mutate: bool):
    # Tree structure:
    #         0
    #       /   \
    #      1     2
    #     / \
    #    3   4
    #       / \
    #      5   6

    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_list": [
                "[None]",
                "[0]",
                "[0]",
                "[1]",
                "[1]",
                "[4]",
                "[4]",
            ],
            "origin_time": [0, 10, 200, 30, 40, 50, 60],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    phylogeny_df.copy()
    result_df = alifestd_mark_clade_logistic_growth_children_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[0, "clade_logistic_growth_children"] > 0
    assert result_df.loc[1, "clade_logistic_growth_children"] > 0
    assert math.isnan(result_df.loc[2, "clade_logistic_growth_children"])
    assert math.isnan(result_df.loc[3, "clade_logistic_growth_children"])
    assert result_df.loc[4, "clade_logistic_growth_children"] > 0
    assert math.isnan(result_df.loc[5, "clade_logistic_growth_children"])
    assert math.isnan(result_df.loc[6, "clade_logistic_growth_children"])


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple6(apply: typing.Callable, mutate: bool):
    # Chain tree: 0
    phylogeny_df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_list": ["[None]"],
            "origin_time": [0],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_clade_logistic_growth_children_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert math.isnan(result_df.loc[0, "clade_logistic_growth_children"])

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple7(apply: typing.Callable, mutate: bool):
    # Tree structure:
    #         0
    #       /   \
    #      1     2
    #     / \
    #    3   4
    #       / \
    #      5   6

    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_list": [
                "[None]",
                "[0]",
                "[0]",
                "[1]",
                "[1]",
                "[4]",
                "[4]",
            ],
            "origin_time": [
                0,
                10,
                20,
                30,
                40,
                50,
                60,
            ],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_clade_logistic_growth_children_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[0, "clade_logistic_growth_children"] < 0
    assert result_df.loc[1, "clade_logistic_growth_children"] > 0
    assert math.isnan(result_df.loc[2, "clade_logistic_growth_children"])
    assert math.isnan(result_df.loc[3, "clade_logistic_growth_children"])
    assert result_df.loc[4, "clade_logistic_growth_children"] > 0
    assert math.isnan(result_df.loc[5, "clade_logistic_growth_children"])
    assert math.isnan(result_df.loc[6, "clade_logistic_growth_children"])

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple8(mutate: bool):
    # Chain tree: 0
    phylogeny_df = pd.DataFrame(
        {
            "id": [1],
            "ancestor_list": ["[None]"],
            "origin_time": [0],
        },
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_clade_logistic_growth_children_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert math.isnan(result_df.loc[1, "clade_logistic_growth_children"])

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple9(apply: typing.Callable, mutate: bool):
    # Tree structure:
    #         0
    #       /   \
    #      1     2
    #     / \
    #    3   4
    #       / \
    #      5   6

    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_list": [
                "[None]",
                "[0]",
                "[0]",
                "[1]",
                "[1]",
                "[4]",
                "[4]",
            ],
            "origin_time": [0, 10, 5, 30, 40, 50, 60],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    phylogeny_df.copy()
    result_df = alifestd_mark_clade_logistic_growth_children_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[0, "clade_logistic_growth_children"] < 0
    assert result_df.loc[1, "clade_logistic_growth_children"] > 0
    assert math.isnan(result_df.loc[2, "clade_logistic_growth_children"])
    assert math.isnan(result_df.loc[3, "clade_logistic_growth_children"])
    assert result_df.loc[4, "clade_logistic_growth_children"] > 0
    assert math.isnan(result_df.loc[5, "clade_logistic_growth_children"])
    assert math.isnan(result_df.loc[6, "clade_logistic_growth_children"])


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple10(apply: typing.Callable, mutate: bool):
    # Tree structure:
    #         0
    #       /   \
    #      1     2
    #     / \
    #    3   4
    #       / \
    #      5   6

    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_list": [
                "[None]",
                "[0]",
                "[0]",
                "[1]",
                "[1]",
                "[4]",
                "[4]",
            ],
            "origin_time": [
                10,
                10,
                10,
                10,
                10,
                10,
                10,
            ],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_clade_logistic_growth_children_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    _0 = pytest.approx(0, abs=1e-3)
    assert result_df.loc[0, "clade_logistic_growth_children"] == _0
    assert result_df.loc[1, "clade_logistic_growth_children"] == _0
    assert math.isnan(result_df.loc[2, "clade_logistic_growth_children"])
    assert math.isnan(result_df.loc[3, "clade_logistic_growth_children"])
    assert result_df.loc[4, "clade_logistic_growth_children"] == _0
    assert math.isnan(result_df.loc[5, "clade_logistic_growth_children"])
    assert math.isnan(result_df.loc[6, "clade_logistic_growth_children"])

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple11(apply: typing.Callable, mutate: bool):
    # Tree structure:
    #         0             7
    #       /   \          / \
    #      1     2        8   9
    #     / \
    #    3   4
    #       / \
    #      5   6

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
    with pytest.raises(ValueError):
        alifestd_mark_clade_logistic_growth_children_asexual(
            phylogeny_df,
            mutate=mutate,
        )

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple12(mutate: bool):
    # Tree structure:
    #        |---- 4
    #   |--- 0 --- 3
    #   1
    #   |--- 2
    phylogeny_df = pd.DataFrame(
        {
            "id": [3, 0, 1, 2, 4],
            "ancestor_list": ["[0]", "[1]", "[None]", "[1]", "[0]"],
            "origin_time": [50, 0, 20, 100, 40],
        },
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_clade_logistic_growth_children_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert math.isnan(result_df.loc[3, "clade_logistic_growth_children"])
    assert result_df.loc[0, "clade_logistic_growth_children"] < 0
    assert result_df.loc[1, "clade_logistic_growth_children"] > 0
    assert math.isnan(result_df.loc[2, "clade_logistic_growth_children"])
    assert math.isnan(result_df.loc[4, "clade_logistic_growth_children"])

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple13(mutate: bool):
    # Tree structure:
    #        |---- 4
    #   |--- 0 --- 3
    #   1
    #   |--- 22
    phylogeny_df = pd.DataFrame(
        {
            "id": [3, 0, 1, 22, 4],
            "ancestor_list": ["[0]", "[1]", "[None]", "[1]", "[0]"],
            "origin_time": [50, 0, 20, 10, 40],
        },
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_clade_logistic_growth_children_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert math.isnan(result_df.loc[3, "clade_logistic_growth_children"])
    assert result_df.loc[0, "clade_logistic_growth_children"] < 0
    assert result_df.loc[1, "clade_logistic_growth_children"] < 0
    assert math.isnan(result_df.loc[22, "clade_logistic_growth_children"])
    assert math.isnan(result_df.loc[4, "clade_logistic_growth_children"])

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple14(mutate: bool):
    # Tree structure:
    #        |---- 4
    #   |--- 100 --- 3
    #   1
    #   |--- 22
    phylogeny_df = pd.DataFrame(
        {
            "id": [3, 100, 1, 22, 4],
            "ancestor_list": ["[100]", "[1]", "[None]", "[1]", "[100]"],
            "origin_time": [50, 0, 20, 10, 40],
        },
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_clade_logistic_growth_children_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert math.isnan(result_df.loc[3, "clade_logistic_growth_children"])
    assert result_df.loc[100, "clade_logistic_growth_children"] < 0
    assert result_df.loc[1, "clade_logistic_growth_children"] > 0
    assert math.isnan(result_df.loc[22, "clade_logistic_growth_children"])
    assert math.isnan(result_df.loc[4, "clade_logistic_growth_children"])

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple15(apply: typing.Callable, mutate: bool):
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
            "origin_time": [0, 10, 20, 30, 40, 50, 60],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_clade_logistic_growth_children_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[0, "clade_logistic_growth_children"] > 0
    assert result_df.loc[1, "clade_logistic_growth_children"] > 0
    assert result_df.loc[2, "clade_logistic_growth_children"] > 0
    assert math.isnan(result_df.loc[3, "clade_logistic_growth_children"])
    assert math.isnan(result_df.loc[4, "clade_logistic_growth_children"])
    assert math.isnan(result_df.loc[5, "clade_logistic_growth_children"])
    assert math.isnan(result_df.loc[6, "clade_logistic_growth_children"])

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
    if "origin_time" not in phylogeny_df.columns:
        phylogeny_df["origin_time"] = phylogeny_df["id"]

    phylogeny_df = alifestd_splay_polytomies(phylogeny_df)
    phylogeny_df = alifestd_collapse_unifurcations(phylogeny_df)
    phylogeny_df = alifestd_delete_unifurcating_roots_asexual(phylogeny_df)
    original = phylogeny_df.copy()

    result_df = alifestd_mark_clade_logistic_growth_children_asexual(
        phylogeny_df
    )

    # Confirm that the input dataframe is not mutated.
    assert original.equals(phylogeny_df)

    # Verify result_df
    assert "clade_logistic_growth_children" in result_df.columns
    assert len(result_df) == len(phylogeny_df)

    result_df = alifestd_mark_leaves(result_df)
    assert (
        result_df["clade_logistic_growth_children"].isna()
        == result_df["is_leaf"]
    ).all()
