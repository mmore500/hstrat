import os
import typing

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_make_empty,
    alifestd_screen_trait_defined_clades_naive_asexual,
    alifestd_to_working_format,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def test_empty():
    phylogeny_df = alifestd_make_empty()
    phylogeny_df["origin_time"] = None
    res = alifestd_screen_trait_defined_clades_naive_asexual(
        phylogeny_df,
        mask_trait_absent=[],
        mask_trait_present=[],
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
        alifestd_screen_trait_defined_clades_naive_asexual(
            phylogeny_df,
            mutate=mutate,
            mask_trait_absent=[True, False, False],
            mask_trait_present=[False, False, True],
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
    result = alifestd_screen_trait_defined_clades_naive_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_present=[False, False, False, True, False],
        mask_trait_absent=[True, False, False, False, True],
    )
    assert not result[0]
    assert not result[1]
    assert not result[2]
    assert result[3]
    assert not result[4]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple3(apply: typing.Callable, mutate: bool):
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
    result = alifestd_screen_trait_defined_clades_naive_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_absent=[False, False, False, True, True, False, False],
        mask_trait_present=[False, True, False, False, False, True, True],
        defining_mut_thresh=0.95,
        defining_mut_sister_thresh=0.5,
    )
    assert not result[0]
    assert not result[1]
    assert result[2]
    assert not result[3]
    assert not result[4]
    assert not result[5]
    assert not result[6]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple4(apply: typing.Callable, mutate: bool):
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
    result = alifestd_screen_trait_defined_clades_naive_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_present=[
            False,
            False,
            True,
            True,
            False,
            True,
            True,
            True,
            True,
            False,
        ],
        mask_trait_absent=[
            True,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            True,
        ],
    )
    assert not result[0]
    assert not result[1]
    assert not result[2]
    assert not result[3]
    assert not result[4]
    assert not result[5]
    assert not result[6]
    assert not result[7]
    assert result[8]
    assert not result[9]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple5(apply: typing.Callable, mutate: bool):
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
    result = alifestd_screen_trait_defined_clades_naive_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_absent=[False, False, False, True, True, False, False],
        mask_trait_present=[False, True, False, False, False, True, True],
        defining_mut_thresh=0.95,
        defining_mut_sister_thresh=0.3,
    )
    assert not result[0]
    assert not result[1]
    assert not result[2]
    assert not result[3]
    assert not result[4]
    assert not result[5]
    assert not result[6]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple6(apply: typing.Callable, mutate: bool):
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
    result = alifestd_screen_trait_defined_clades_naive_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_absent=[False, False, False, True, True, False, True],
        mask_trait_present=[False, True, False, False, False, True, False],
        defining_mut_thresh=0.95,
        defining_mut_sister_thresh=0.6,
    )
    assert not result[0]
    assert not result[1]
    assert not result[2]
    assert not result[3]
    assert not result[4]
    assert result[5]
    assert not result[6]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple7(apply: typing.Callable, mutate: bool):
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
    result = alifestd_screen_trait_defined_clades_naive_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_absent=[False, False, False, True, True, False, True],
        mask_trait_present=[False, True, False, False, False, True, False],
        defining_mut_thresh=0.95,
        defining_mut_sister_thresh=-0.1,
    )
    assert not result[0]
    assert not result[1]
    assert not result[2]
    assert not result[3]
    assert not result[4]
    assert not result[5]
    assert not result[6]

    if not mutate:
        assert original_df.equals(phylogeny_df)
