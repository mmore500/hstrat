import os
import typing

import numpy as np
import pandas as pd
import pytest
from scipy import stats as scipy_stats

from hstrat._auxiliary_lib import (
    alifestd_make_empty,
    alifestd_screen_trait_defined_clades_fisher_asexual,
    alifestd_to_working_format,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def approx_scipy_fisher(contingency_table: np.ndarray) -> pytest.approx:
    __, p_value = scipy_stats.fisher_exact(
        contingency_table, alternative="greater"
    )
    return pytest.approx(p_value)


def test_empty():
    phylogeny_df = alifestd_make_empty()
    phylogeny_df["origin_time"] = None
    res = alifestd_screen_trait_defined_clades_fisher_asexual(
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
        alifestd_screen_trait_defined_clades_fisher_asexual(
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
    result = alifestd_screen_trait_defined_clades_fisher_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_present=[False, False, False, False, True],
        mask_trait_absent=[True, False, False, True, False],
    )
    assert result[0] == approx_scipy_fisher([[0, 1], [1, 0]])
    assert result[1] == approx_scipy_fisher([[1, 1], [0, 1]])
    assert result[2] == approx_scipy_fisher([[1, 2], [1, 2]])
    assert result[3] == approx_scipy_fisher([[0, 1], [1, 1]])
    assert result[4] == approx_scipy_fisher([[1, 0], [0, 1]])

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
    result = alifestd_screen_trait_defined_clades_fisher_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_absent=[False, False, True, False, False, True, True],
        mask_trait_present=[False, True, False, True, True, False, False],
    )
    assert result[0] == approx_scipy_fisher([[3, 3], [3, 3]])
    assert result[0] >= 0.5
    assert result[1] == approx_scipy_fisher([[3, 0], [0, 3]])
    assert result[1] < 0.5
    assert result[2] == approx_scipy_fisher([[0, 3], [3, 0]])
    assert result[2] > 0.5
    assert result[3] == approx_scipy_fisher([[1, 0], [1, 0]])
    assert result[4] == approx_scipy_fisher([[1, 0], [1, 0]])
    assert result[5] == approx_scipy_fisher([[0, 1], [0, 1]])
    assert result[6] == approx_scipy_fisher([[0, 1], [0, 1]])

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
    result = alifestd_screen_trait_defined_clades_fisher_asexual(
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
    assert result[0] == approx_scipy_fisher([[4, 1], [4, 1]])
    assert result[1] == approx_scipy_fisher([[3, 0], [1, 0]])
    assert result[2] == approx_scipy_fisher([[1, 0], [3, 0]])
    assert result[3] == approx_scipy_fisher([[1, 0], [2, 0]])
    assert result[4] == approx_scipy_fisher([[2, 0], [1, 0]])
    assert result[5] == approx_scipy_fisher([[1, 0], [1, 0]])
    assert result[6] == approx_scipy_fisher([[1, 0], [1, 0]])
    assert result[7] == approx_scipy_fisher([[1, 0], [1, 0]])
    assert result[8] == approx_scipy_fisher([[0, 0], [0, 0]])
    assert result[9] == approx_scipy_fisher([[0, 0], [0, 0]])

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple6(apply: typing.Callable, mutate: bool):
    # Chain tree: 0 -> 1 -> 2
    phylogeny_df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_list": ["[None]"],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result = alifestd_screen_trait_defined_clades_fisher_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_absent=[True],
        mask_trait_present=[False],
    )
    assert result[0] == approx_scipy_fisher([[0, 1], [0, 1]])
    assert result[0] >= 0.5

    if not mutate:
        assert original_df.equals(phylogeny_df)
