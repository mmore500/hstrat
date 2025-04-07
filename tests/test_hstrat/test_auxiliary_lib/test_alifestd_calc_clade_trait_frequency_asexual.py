import math
import os
import typing

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_calc_clade_trait_frequency_asexual,
    alifestd_make_empty,
    alifestd_to_working_format,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def test_empty():
    phylogeny_df = alifestd_make_empty()
    phylogeny_df["origin_time"] = None
    res = alifestd_calc_clade_trait_frequency_asexual(
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
    result = alifestd_calc_clade_trait_frequency_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_absent=[True, False, False],
        mask_trait_present=[False, False, True],
    )
    assert result[0] == 0.5
    assert result[1] == 1.0
    assert result[2] == 1.0

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
    result = alifestd_calc_clade_trait_frequency_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_present=[False, False, False, False, True],
        mask_trait_absent=[True, False, False, True, False],
    )
    assert result[0] == 0.0
    assert result[1] == 0.5
    assert result[2] == pytest.approx(1 / 3)
    assert result[3] == 0.0
    assert result[4] == 1.0

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
    result = alifestd_calc_clade_trait_frequency_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_absent=[False, False, False, False, True, False, False],
        mask_trait_present=[False, False, False, True, False, True, True],
    )
    assert result[0] == 0.75
    assert result[1] == 0.5
    assert result[2] == 1.0
    assert result[3] == 1.0
    assert result[4] == 0.0
    assert result[5] == 1.0
    assert result[6] == 1.0

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
    result = alifestd_calc_clade_trait_frequency_asexual(
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
            False,
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
            False,
        ],
    )
    assert result[0] == pytest.approx(4 / 5)
    assert result[1] == 1.0
    assert result[2] == 1.0
    assert result[3] == 1.0
    assert result[4] == 1.0
    assert result[5] == 1.0
    assert result[6] == 1.0
    assert result[7] == 1.0
    assert math.isnan(result[8])
    assert math.isnan(result[9])

    if not mutate:
        assert original_df.equals(phylogeny_df)
