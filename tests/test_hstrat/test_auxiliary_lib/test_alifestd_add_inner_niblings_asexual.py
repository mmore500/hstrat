import pandas as pd
import pandas.testing as pdt
import pytest

from hstrat._auxiliary_lib import (
    alifestd_add_inner_niblings_asexual,
    alifestd_make_empty,
)


def test_empty_df():
    df = alifestd_make_empty()
    result = alifestd_add_inner_niblings_asexual(df)
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
    result = alifestd_add_inner_niblings_asexual(df)

    expected = pd.DataFrame(
        {
            "id": [0],
            "ancestor_id": [0],
            "origin_time": [0],
            "is_root": [True],
        },
    )
    pdt.assert_frame_equal(result[expected.columns], expected, check_like=True)


@pytest.mark.parametrize("mutate", [False, True])
def test_internal_node_add_leaves(mutate: bool):
    # Simple chain: 0 -> 1 -> 2
    df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 1],
            "origin_time": [0, 1, 2],
        },
    )
    original = df.copy()
    result = alifestd_add_inner_niblings_asexual(df, mutate=mutate)
    assert mutate or df.equals(original)

    expected = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_id": [3, 4, 1, 3, 0, 3, 4],
            "origin_time": [0, 1, 2, 0, 1, 0, 1],
        },
    )
    pdt.assert_frame_equal(
        result[expected.columns].sort_values(by="id").reset_index(drop=True),
        expected,
        check_like=True,
    )


@pytest.mark.parametrize("mutate", [False, True])
def test_add_inner_niblings_ancestor_list(mutate: bool):
    df_list = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_id": [0, 0],
            "ancestor_list": ["[none]", "[0]"],
        }
    )

    original = df_list.copy()
    result = alifestd_add_inner_niblings_asexual(df_list, mutate=mutate)
    assert mutate or original.equals(df_list)

    expected = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [2, 0, 2, 2],
            "ancestor_list": ["[2]", "[0]", "[none]", "[2]"],
        },
    )
    pdt.assert_frame_equal(
        result[expected.columns].sort_values(by="id").reset_index(drop=True),
        expected,
        check_like=True,
    )


@pytest.mark.parametrize("mutate", [False, True])
def test_add_inner_niblings_ancestor_list_only1(mutate: bool):
    df_list = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[none]", "[none]"],
        }
    )

    original = df_list.copy()
    result = alifestd_add_inner_niblings_asexual(df_list, mutate=False)
    assert mutate or original.equals(df_list)

    expected = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[none]", "[none]"],
        },
    )
    pdt.assert_frame_equal(
        result[expected.columns].sort_values(by="id").reset_index(drop=True),
        expected,
        check_like=True,
    )


@pytest.mark.parametrize("mutate", [False, True])
def test_add_inner_niblings_ancestor_list_only2(mutate: bool):
    df_list = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[none]", "[0]"],
        }
    )

    original = df_list.copy()
    result = alifestd_add_inner_niblings_asexual(df_list, mutate=False)
    assert mutate or original.equals(df_list)

    expected = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [2, 0, 2, 2],
            "ancestor_list": ["[2]", "[0]", "[none]", "[2]"],
        },
    )
    pdt.assert_frame_equal(
        result[expected.columns].sort_values(by="id").reset_index(drop=True),
        expected,
        check_like=True,
    )


@pytest.mark.parametrize("mutate", [False, True])
def test_bifurcation_add_inner_niblings(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 0],
            "origin_time": [0, 1, 1],
        }
    )
    original = df.copy()
    result = alifestd_add_inner_niblings_asexual(df, mutate=mutate)
    assert mutate or df.equals(original)

    expected = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [3, 0, 0, 3, 3],
            "origin_time": [0, 1, 1, 0, 0],
        }
    )
    pdt.assert_frame_equal(
        result[expected.columns].sort_values(by="id").reset_index(drop=True),
        expected,
        check_like=True,
    )


@pytest.mark.parametrize("mutate", [False, True])
def test_multifurcation_add_inner_niblings(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 0, 0],
            "origin_time": [0, 1, 1, 1],
        }
    )
    original = df.copy()
    result = alifestd_add_inner_niblings_asexual(df, mutate=mutate)
    assert mutate or df.equals(original)

    expected = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_id": [4, 0, 0, 0, 4, 4],
            "origin_time": [0, 1, 1, 1, 0, 0],
        }
    )
    pdt.assert_frame_equal(
        result[expected.columns].sort_values(by="id").reset_index(drop=True),
        expected,
        check_like=True,
    )


@pytest.mark.parametrize("mutate", [False, True])
def test_nested_bifurcations_add_inner_niblings(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [5, 1, 2, 3, 4],
            "ancestor_id": [5, 5, 5, 2, 2],
            "origin_time": [0, 1, 1, 2, 2],
        }
    )
    original = df.copy()
    result = alifestd_add_inner_niblings_asexual(df, mutate=mutate)
    assert mutate or df.equals(original)

    expected = pd.DataFrame(
        {
            "id": [5, 1, 2, 3, 4, 11, 8, 17, 14],
            "ancestor_id": [11, 5, 8, 2, 2, 11, 5, 11, 8],
            "origin_time": [0, 1, 1, 2, 2, 0, 1, 0, 1],
        }
    )
    pdt.assert_frame_equal(
        result[expected.columns].sort_values(by="id").reset_index(drop=True),
        expected.sort_values(by="id").reset_index(drop=True),
        check_like=True,
    )
