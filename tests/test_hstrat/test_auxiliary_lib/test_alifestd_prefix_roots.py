import pandas as pd
import pandas.testing as pdt
import pytest

from hstrat._auxiliary_lib import alifestd_make_empty, alifestd_prefix_roots


def test_empty_df():
    df = alifestd_make_empty()
    result = alifestd_prefix_roots(df)
    assert result.empty


@pytest.mark.parametrize("mutate", [False, True])
def test_single_root_with_origin_time(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0],
            "origin_time": [10],
            "ancestor_id": [0],
            "ancestor_list": ["[none]"],
        }
    )
    original = df.copy()

    result = alifestd_prefix_roots(df, origin_time=5, mutate=mutate)
    if not mutate:
        pdt.assert_frame_equal(df, original)

    expected = pd.DataFrame(
        {
            "id": [0, 1],
            "origin_time": [10, 5],
            "ancestor_id": [1, 1],
            "ancestor_list": ["[1]", "[]"],
        }
    )
    pdt.assert_frame_equal(
        result.reset_index(drop=True), expected, check_like=True
    )


@pytest.mark.parametrize("mutate", [False, True])
def test_single_root_without_origin_time(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0],
            "origin_time": [10],
            "ancestor_id": [0],
            "ancestor_list": ["[none]"],
        }
    )
    original = df.copy()
    result = alifestd_prefix_roots(df, origin_time=None, mutate=mutate)
    if not mutate:
        pdt.assert_frame_equal(df, original)

    expected = pd.DataFrame(
        {
            "id": [0, 1],
            "origin_time": [10, 0],
            "ancestor_id": [1, 1],
            "ancestor_list": ["[1]", "[]"],
        }
    )
    pdt.assert_frame_equal(
        result.reset_index(drop=True), expected, check_like=True
    )


@pytest.mark.parametrize("mutate", [False, True])
def test_multiple_roots(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "origin_time": [20, 15, 10, 5],
            "ancestor_id": [0, 0, 2, 2],
            "ancestor_list": ["[none]", "[0]", "[none]", "[2]"],
        }
    )
    original = df.copy()
    result = alifestd_prefix_roots(df, origin_time=12, mutate=mutate)
    if not mutate:
        pdt.assert_frame_equal(df, original)

    expected = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "origin_time": [20, 15, 10, 5, 12],
            "ancestor_id": [4, 0, 2, 2, 4],
            "ancestor_list": ["[4]", "[0]", "[none]", "[2]", "[]"],
        }
    )
    pdt.assert_frame_equal(
        result.reset_index(drop=True), expected, check_like=True
    )


@pytest.mark.parametrize("mutate", [False, True])
def test_no_eligible_roots(mutate: bool):

    df = pd.DataFrame(
        {
            "id": [0, 1],
            "origin_time": [10, 5],
            "ancestor_id": [0, 0],
            "ancestor_list": ["[none]", "[0]"],
        }
    )
    original = df.copy()
    result = alifestd_prefix_roots(df, origin_time=15, mutate=mutate)
    if not mutate:
        pdt.assert_frame_equal(df, original)

    pdt.assert_frame_equal(
        result.reset_index(drop=True),
        original.reset_index(drop=True),
        check_like=True,
    )


@pytest.mark.parametrize("mutate", [False, True])
def test_warn_on_origin_time_delta(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0],
            "origin_time": [10],
            "origin_time_delta": [5],
            "ancestor_id": [0],
            "ancestor_list": ["[none]"],
        }
    )
    original = df.copy()
    with pytest.warns(UserWarning):
        alifestd_prefix_roots(df, origin_time=5, mutate=mutate)
    if not mutate:
        pdt.assert_frame_equal(df, original)
