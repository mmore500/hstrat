import pandas as pd
import pandas.testing as pdt
import pytest

from hstrat._auxiliary_lib import (
    alifestd_add_inner_leaves,
    alifestd_make_empty,
)


def test_empty_df():
    df = alifestd_make_empty()
    result = alifestd_add_inner_leaves(df)
    assert result.empty


def test_single_node_df():
    df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_id": [0],
            "origin_time": [0],
            "is_root": [True],
        },
    )
    result = alifestd_add_inner_leaves(df)

    expected = pd.DataFrame(
        {
            "id": [0],
            "ancestor_id": [0],
            "origin_time": [0],
            "is_leaf": [True],
            "is_root": [True],
        },
    )
    pdt.assert_frame_equal(result, expected, check_like=True)


@pytest.mark.parametrize("mutate", [False, True])
def test_internal_node_add_leaves(mutate: bool):
    # Simple chain: 0 -> 1 -> 2
    df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 1],
            "is_root": [True, False, False],
            "origin_time_delta": [1, 1, 1],
        },
    )
    original = df.copy()
    result = alifestd_add_inner_leaves(df, mutate=mutate)
    assert mutate or df.equals(original)

    expected = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 1, 0, 1],
            "is_leaf": [False, False, True, True, True],
            "is_root": [True, False, False, False, False],
            "origin_time_delta": [1, 1, 1, 0, 0],
        },
    )
    pdt.assert_frame_equal(result, expected, check_like=True)


@pytest.mark.parametrize("mutate", [False, True])
def test_ancestor_id_only(mutate: bool):
    df_id = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 0],
            "is_leaf": [False, True, True],
            "is_root": [True, False, False],
        }
    )

    original = df_id.copy()
    result = alifestd_add_inner_leaves(df_id, mutate=mutate)
    assert mutate or original.equals(df_id)

    expected_id = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 0, 0],
            "is_leaf": [False, True, True, True],
            "is_root": [True, False, False, False],
        }
    )

    pdt.assert_frame_equal(result, expected_id)


@pytest.mark.parametrize("mutate", [False, True])
def test_add_inner_leaves_ancestor_list(mutate: bool):
    df_list = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_id": [0, 0],
            "ancestor_list": ["[none]", "[0]"],
            "is_leaf": [False, True],
            "is_root": [True, False],
        }
    )

    original = df_list.copy()
    result = alifestd_add_inner_leaves(df_list, mutate=mutate)
    assert mutate or original.equals(df_list)

    expected_list = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 0],
            "ancestor_list": ["[none]", "[0]", "[0]"],
            "is_leaf": [False, True, True],
            "is_root": [True, False, False],
        }
    )

    pdt.assert_frame_equal(result.reset_index(drop=True), expected_list)


@pytest.mark.parametrize("mutate", [False, True])
def test_add_inner_leaves_ancestor_list_only1(mutate: bool):
    df_list = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[none]", "[none]"],
        }
    )

    original = df_list.copy()
    result = alifestd_add_inner_leaves(df_list, mutate=False)
    assert mutate or original.equals(df_list)

    expected_list = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[none]", "[none]"],
            "is_leaf": [True, True],
        }
    )

    pdt.assert_frame_equal(result, expected_list)


@pytest.mark.parametrize("mutate", [False, True])
def test_add_inner_leaves_ancestor_list_only2(mutate: bool):
    df_list = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[none]", "[0]"],
        }
    )

    original = df_list.copy()
    result = alifestd_add_inner_leaves(df_list, mutate=False)
    assert mutate or original.equals(df_list)

    expected_list = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[none]", "[0]", "[0]"],
            "is_leaf": [False, True, True],
        }
    )

    pdt.assert_frame_equal(result, expected_list)
