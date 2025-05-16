import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_collapse_unifurcations,
    alifestd_count_unifurcating_roots_asexual,
)

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_count_unifurcating_roots_asexual_simple1(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_list": ["[]"],
        }
    )
    original_df = df.copy()
    assert alifestd_count_unifurcating_roots_asexual(df, mutate=mutate) == 0

    if not mutate:
        assert original_df.equals(df)


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_count_unifurcating_roots_asexual_simple2(
    mutate: bool,
):
    df = pd.DataFrame(
        {
            "id": [0, 8],
            "ancestor_id": [0, 0],
            "ancestor_list": ["[none]", "[0]"],
        }
    )
    original_df = df.copy()
    assert alifestd_count_unifurcating_roots_asexual(df, mutate=mutate) == 1

    expected = pd.DataFrame(
        {
            "id": [8],
            "ancestor_id": [8],
            "ancestor_list": ["[]"],
        }
    )
    assert alifestd_count_unifurcating_roots_asexual(expected) == 0

    if not mutate:
        assert original_df.equals(df)


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_count_unifurcating_roots_asexual_simple3(
    mutate: bool,
):
    df = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_id": [0, 0],
        }
    )
    original_df = df.copy()
    assert alifestd_count_unifurcating_roots_asexual(df, mutate=mutate) == 1

    expected = pd.DataFrame(
        {
            "id": [1],
            "ancestor_id": [1],
        }
    )
    assert alifestd_count_unifurcating_roots_asexual(expected) == 0

    if not mutate:
        assert original_df.equals(df)


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_count_unifurcating_roots_asexual_simple4(
    mutate: bool,
):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 0],
            "ancestor_list": ["[none]", "[0]", "[0]"],
        }
    )
    original_df = df.copy()
    assert alifestd_count_unifurcating_roots_asexual(df, mutate=mutate) == 0

    if not mutate:
        assert df.equals(original_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_count_unifurcating_roots_asexual_simple5(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 4, 3, 5],
            "ancestor_id": [0, 0, 1, 2, 0, 5],
            "ancestor_list": ["[none]", "[0]", "[1]", "[2]", "[0]", "[none]"],
            "asdf": ["a", "b", "c", "d", "e", "f"],
        }
    )
    original_df = df.copy()
    assert alifestd_count_unifurcating_roots_asexual(df, mutate=mutate) == 0

    if not mutate:
        assert df.equals(original_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_count_unifurcating_roots_asexual_simple6(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_id": [0, 0, 1, 2, 3, 4, 5],
            "origin_time": [0, 0, 1, 2, 3, 4, 5],
        }
    )
    original_df = df.copy()
    assert alifestd_count_unifurcating_roots_asexual(df, mutate=mutate) == 1

    expected = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 6],
            "ancestor_id": [1, 1, 2, 3, 4, 5],
            "origin_time": [0, 1, 2, 3, 4, 5],
        }
    )
    assert alifestd_count_unifurcating_roots_asexual(expected) == 1

    assert (
        alifestd_count_unifurcating_roots_asexual(
            alifestd_collapse_unifurcations(df, mutate=mutate),
        )
        == 1
    )

    if not mutate:
        assert df.equals(original_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_count_unifurcating_roots_asexual_simple7(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_id": [0, 0, 1, 2, 3, 4, 0],
            "asdf": [True, True, True, False, True, True, False],
        }
    )
    original_df = df.copy()
    assert alifestd_count_unifurcating_roots_asexual(df, mutate=mutate) == 0

    if not mutate:
        assert df.equals(original_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_count_unifurcating_roots_asexual_simple8(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 4, 3, 5, 6],
            "ancestor_id": [0, 0, 1, 2, 2, 5, 5],
            "asdf": ["a", "b", "c", "d", "e", "f", "g"],
        }
    )
    original_df = df.copy()
    assert alifestd_count_unifurcating_roots_asexual(df, mutate=mutate) == 2

    if not mutate:
        assert df.equals(original_df)
