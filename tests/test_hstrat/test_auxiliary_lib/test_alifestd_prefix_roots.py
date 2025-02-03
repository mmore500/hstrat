import pandas as pd
import pandas.testing as pdt
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_make_empty,
    alifestd_prefix_roots,
    alifestd_prefix_roots_polars,
)


def test_empty_df():
    df = alifestd_make_empty()
    result = alifestd_prefix_roots(df)
    assert result.empty

    with pytest.raises(NotImplementedError):
        alifestd_prefix_roots_polars(pl.from_pandas(df))


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

    with pytest.raises(NotImplementedError):
        alifestd_prefix_roots_polars(pl.from_pandas(original))
    df.drop(columns=["ancestor_list"], inplace=True)
    with pytest.raises(NotImplementedError):
        alifestd_prefix_roots_polars(pl.from_pandas(original), origin_time=5)


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

    with pytest.raises(NotImplementedError):
        alifestd_prefix_roots_polars(pl.from_pandas(original))
    df.drop(columns=["ancestor_list"], inplace=True)
    with pytest.raises(NotImplementedError):
        alifestd_prefix_roots_polars(
            pl.from_pandas(original), origin_time=None
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

    with pytest.raises(NotImplementedError):
        alifestd_prefix_roots_polars(pl.from_pandas(original))
    df.drop(columns=["ancestor_list"], inplace=True)
    with pytest.raises(NotImplementedError):
        alifestd_prefix_roots_polars(pl.from_pandas(original), origin_time=12)


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

    with pytest.raises(NotImplementedError):
        alifestd_prefix_roots_polars(pl.from_pandas(original))
    df.drop(columns=["ancestor_list"], inplace=True)
    with pytest.raises(NotImplementedError):
        alifestd_prefix_roots_polars(pl.from_pandas(original), origin_time=15)


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

    with pytest.raises(NotImplementedError):
        alifestd_prefix_roots_polars(pl.from_pandas(original))
    df.drop(columns=["ancestor_list"], inplace=True)
    with pytest.raises(NotImplementedError):
        alifestd_prefix_roots_polars(pl.from_pandas(original), origin_time=5)


@pytest.mark.parametrize("mutate", [False, True])
def test_fast_path_single_root(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "origin_time": [10, 9, 8],
            "ancestor_id": [0, 0, 1],
            "is_root": [True, False, False],
        },
    )
    original = df.copy()
    result = alifestd_prefix_roots(
        df,
        allow_id_reassign=True,
        origin_time=5,
        mutate=mutate,
    )
    if not mutate:
        pdt.assert_frame_equal(df, original)

    expected = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "origin_time": [5, 10, 9, 8],
            "ancestor_id": [0, 0, 1, 2],
        }
    )
    pdt.assert_frame_equal(
        result.reset_index(drop=True), expected, check_like=True
    )

    pdt.assert_frame_equal(
        result.reset_index(drop=True),
        alifestd_prefix_roots_polars(
            pl.from_pandas(original), allow_id_reassign=True, origin_time=5
        ).to_pandas(),
        check_dtype=False,
    )


@pytest.mark.parametrize("mutate", [False, True])
def test_fast_path_multiple_roots(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "origin_time": [15, 22, 29, 28, 8, 9, 10],
            "ancestor_id": [0, 0, 1, 1, 4, 4, 4],
        },
    )
    original = df.copy()
    result = alifestd_prefix_roots(
        df,
        allow_id_reassign=True,
        origin_time=10,
        mutate=mutate,
    )
    if not mutate:
        pdt.assert_frame_equal(df, original)

    expected = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6, 7],
            "origin_time": [10, 15, 22, 29, 28, 8, 9, 10],
            "ancestor_id": [0, 0, 1, 2, 2, 5, 5, 5],
        },
    )
    pdt.assert_frame_equal(
        result.reset_index(drop=True), expected, check_like=True
    )

    pdt.assert_frame_equal(
        result.reset_index(drop=True),
        alifestd_prefix_roots_polars(
            pl.from_pandas(original), allow_id_reassign=True, origin_time=10
        ).to_pandas(),
        check_dtype=False,
    )


@pytest.mark.parametrize("mutate", [False, True])
def test_fast_path_no_eligible_roots(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "origin_time": [5, 4, 3],
            "ancestor_id": [0, 0, 1],
        }
    )
    original = df.copy()
    result = alifestd_prefix_roots(
        df,
        allow_id_reassign=True,
        origin_time=10,
        mutate=mutate,
    )
    if not mutate:
        pdt.assert_frame_equal(df, original)
    pdt.assert_frame_equal(result, original)

    pdt.assert_frame_equal(
        result.reset_index(drop=True),
        alifestd_prefix_roots_polars(
            pl.from_pandas(original), allow_id_reassign=True, origin_time=10
        ).to_pandas(),
        check_dtype=False,
    )
