import typing

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_make_empty,
    alifestd_mark_num_preceding_leaves_asexual,
    alifestd_to_working_format,
)


def test_empty():
    res = alifestd_mark_num_preceding_leaves_asexual(alifestd_make_empty())
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
        alifestd_mark_num_preceding_leaves_asexual(
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
        },
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_num_preceding_leaves_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[3, "num_preceding_leaves"] == 0
    assert result_df.loc[0, "num_preceding_leaves"] == 0
    assert result_df.loc[1, "num_preceding_leaves"] == 0
    assert result_df.loc[2, "num_preceding_leaves"] == 2
    assert result_df.loc[4, "num_preceding_leaves"] == 1

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
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_num_preceding_leaves_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[0, "num_preceding_leaves"] == 0
    assert result_df.loc[1, "num_preceding_leaves"] == 0
    assert result_df.loc[2, "num_preceding_leaves"] == 2
    assert result_df.loc[3, "num_preceding_leaves"] == 0
    assert result_df.loc[4, "num_preceding_leaves"] == 1
    assert result_df.loc[5, "num_preceding_leaves"] == 2
    assert result_df.loc[6, "num_preceding_leaves"] == 3

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
        },
    )
    phylogeny_df = apply(phylogeny_df)
    phylogeny_df.copy()
    result_df = alifestd_mark_num_preceding_leaves_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[0, "num_preceding_leaves"] == 0
    assert result_df.loc[1, "num_preceding_leaves"] == 0
    assert result_df.loc[2, "num_preceding_leaves"] == 3
    assert result_df.loc[3, "num_preceding_leaves"] == 0
    assert result_df.loc[4, "num_preceding_leaves"] == 1
    assert result_df.loc[5, "num_preceding_leaves"] == 1
    assert result_df.loc[6, "num_preceding_leaves"] == 2


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple6(apply: typing.Callable, mutate: bool):
    # Chain tree: 0
    phylogeny_df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_list": ["[None]"],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_num_preceding_leaves_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[0, "num_preceding_leaves"] == 0

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple7(apply: typing.Callable, mutate: bool):
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
    result_df = alifestd_mark_num_preceding_leaves_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[0, "num_preceding_leaves"] == 0
    assert result_df.loc[1, "num_preceding_leaves"] == 0
    assert result_df.loc[2, "num_preceding_leaves"] == 3
    assert result_df.loc[3, "num_preceding_leaves"] == 0
    assert result_df.loc[4, "num_preceding_leaves"] == 1
    assert result_df.loc[5, "num_preceding_leaves"] == 1
    assert result_df.loc[6, "num_preceding_leaves"] == 2
    assert result_df.loc[7, "num_preceding_leaves"] == 0
    assert result_df.loc[8, "num_preceding_leaves"] == 0
    assert result_df.loc[9, "num_preceding_leaves"] == 1

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple8(mutate: bool):
    # Chain tree: 0
    phylogeny_df = pd.DataFrame(
        {
            "id": [1],
            "ancestor_list": ["[None]"],
        },
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_num_preceding_leaves_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[1, "num_preceding_leaves"] == 0

    if not mutate:
        assert original_df.equals(phylogeny_df)
