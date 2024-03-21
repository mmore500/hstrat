from datetime import datetime
import typing

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_assign_contiguous_ids,
    alifestd_coerce_chronological_consistency,
    alifestd_find_chronological_inconsistency,
    alifestd_make_empty,
    alifestd_try_add_ancestor_id_col,
)

dt_epoch = datetime.utcfromtimestamp


@pytest.mark.parametrize("dtype", ["int", "str", "float", "object"])
def test_coerce_chronological_consistency_empty(dtype: str):
    df = alifestd_make_empty()
    df["origin_time"] = pd.Series(dtype=dtype)
    df_ = df.copy()
    assert alifestd_coerce_chronological_consistency(df).equals(df_)
    assert df.equals(df_)


def test_coerce_chronological_consistency_empty_datetime():
    df = alifestd_make_empty()
    df["origin_time"] = pd.to_datetime(pd.Series())
    df_ = df.copy()
    assert alifestd_coerce_chronological_consistency(df).equals(df_)
    assert df.equals(df_)


@pytest.mark.parametrize("wrap", [int, str, float, lambda x: (x,), dt_epoch])
def test_is_chronologically_ordered_sexual1(wrap: typing.Callable):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 22, 333, 44, 5],
            "ancestor_list": [
                "[333,44]",
                "[333,5]",
                "[333]",
                "[none]",
                "[333]",
                "[none]",
            ],
            "origin_time": [*map(wrap, [5, 5, 2, 1, 2, 0])],
        }
    )

    for phylogeny_df_ in phylogeny_df, alifestd_assign_contiguous_ids(
        phylogeny_df
    ):
        for df in phylogeny_df_, phylogeny_df_.sample(frac=1):
            assert alifestd_find_chronological_inconsistency(df) is None
            df_ = df.copy()
            corrected = alifestd_coerce_chronological_consistency(df)
            assert corrected.reset_index(drop=True).equals(
                df_.reset_index(drop=True),
            )
            assert df.equals(df_)


@pytest.mark.parametrize("wrap", [int, str, float, lambda x: (x,), dt_epoch])
def test_is_chronologically_ordered_sexual2(wrap: typing.Callable):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 22, 333, 44, 5],
            "ancestor_list": [
                "[333,44]",
                "[333,5]",
                "[333]",
                "[none]",
                "[333]",
                "[none]",
            ],
            "origin_time": [*map(wrap, [5, 5, 2, 1, 2, 2])],
        }
    )

    for phylogeny_df_ in phylogeny_df, alifestd_assign_contiguous_ids(
        phylogeny_df
    ):
        for df in phylogeny_df_, phylogeny_df_.sample(frac=1):
            assert alifestd_find_chronological_inconsistency(df) is None
            df_ = df.copy()
            corrected = alifestd_coerce_chronological_consistency(df)
            assert corrected.reset_index(drop=True).equals(
                df_.reset_index(drop=True),
            )
            assert df.equals(df_)


@pytest.mark.parametrize("wrap", [int, str, float, lambda x: (x,), dt_epoch])
def test_is_chronologically_unordered_sexual1(wrap: typing.Callable):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 22, 333, 44, 5],
            "ancestor_list": [
                "[333,44]",
                "[333,5]",
                "[333]",
                "[none]",
                "[333]",
                "[none]",
            ],
            "origin_time": [*map(wrap, [5, 5, 2, 1, 2, 6])],
        }
    )

    for phylogeny_df_ in phylogeny_df, alifestd_assign_contiguous_ids(
        phylogeny_df
    ):
        for df in phylogeny_df_, phylogeny_df_.sample(frac=1):
            assert alifestd_find_chronological_inconsistency(df) is not None
            df_ = df.copy()
            corrected = alifestd_coerce_chronological_consistency(df)
            assert not corrected.equals(df_)
            assert alifestd_find_chronological_inconsistency(corrected) is None
            assert df.equals(df_)


@pytest.mark.parametrize("wrap", [int, str, float, lambda x: (x,), dt_epoch])
def test_is_chronologically_unordered_sexual2(wrap: typing.Callable):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 22, 333, 44, 5],
            "ancestor_list": [
                "[333,44]",
                "[333,5]",
                "[333]",
                "[none]",
                "[333]",
                "[none]",
            ],
            "origin_time": [*map(wrap, [1, 5, 2, 1, 2, 2])],
        }
    )

    for phylogeny_df_ in (
        phylogeny_df,
        alifestd_assign_contiguous_ids(phylogeny_df),
        alifestd_try_add_ancestor_id_col(phylogeny_df),
        alifestd_try_add_ancestor_id_col(
            alifestd_assign_contiguous_ids(phylogeny_df)
        ),
    ):
        for df in phylogeny_df_, phylogeny_df_.sample(frac=1):
            assert alifestd_find_chronological_inconsistency(df) is not None
            df_ = df.copy()
            corrected = alifestd_coerce_chronological_consistency(df)
            assert not corrected.equals(df_)
            assert alifestd_find_chronological_inconsistency(corrected) is None
            assert df.equals(df_)


@pytest.mark.parametrize("wrap", [int, str, float, lambda x: (x,), dt_epoch])
def test_is_chronologically_unordered_sexual3(wrap: typing.Callable):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 22, 333, 44, 5],
            "ancestor_list": [
                "[333,44]",
                "[333,5]",
                "[333]",
                "[none]",
                "[333]",
                "[none]",
            ],
            "origin_time": [*map(wrap, [1, 5, 2, 3, 2, 2])],
        }
    )

    for phylogeny_df_ in (
        phylogeny_df,
        alifestd_assign_contiguous_ids(phylogeny_df),
        alifestd_try_add_ancestor_id_col(phylogeny_df),
        alifestd_try_add_ancestor_id_col(
            alifestd_assign_contiguous_ids(phylogeny_df)
        ),
    ):
        for df in phylogeny_df_, phylogeny_df_.sample(frac=1):
            assert alifestd_find_chronological_inconsistency(df) is not None
            df_ = df.copy()
            corrected = alifestd_coerce_chronological_consistency(df)
            assert not corrected.equals(df_)
            assert alifestd_find_chronological_inconsistency(corrected) is None
            assert df.equals(df_)


@pytest.mark.parametrize("wrap", [int, str, float, lambda x: (x,), dt_epoch])
def test_is_chronologically_ordered_asexual1(wrap: typing.Callable):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 22, 333, 44, 5],
            "ancestor_list": [
                "[44]",
                "[5]",
                "[333]",
                "[none]",
                "[1]",
                "[333]",
            ],
            "origin_time": [*map(wrap, [6, 5, 2, 1, 6, 2])],
        }
    )

    for phylogeny_df_ in (
        phylogeny_df,
        alifestd_assign_contiguous_ids(phylogeny_df),
        alifestd_try_add_ancestor_id_col(phylogeny_df),
        alifestd_try_add_ancestor_id_col(
            alifestd_assign_contiguous_ids(phylogeny_df)
        ),
    ):
        for df in phylogeny_df_, phylogeny_df_.sample(frac=1):
            assert alifestd_find_chronological_inconsistency(df) is None
            df_ = df.copy()
            corrected = alifestd_coerce_chronological_consistency(df)
            assert corrected.reset_index(drop=True).equals(
                df_.reset_index(drop=True),
            )
            assert df.equals(df_)


@pytest.mark.parametrize("wrap", [int, str, float, lambda x: (x,), dt_epoch])
def test_is_chronologically_ordered_asexual2(wrap: typing.Callable):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 22, 333, 44, 5],
            "ancestor_list": [
                "[44]",
                "[5]",
                "[333]",
                "[none]",
                "[1]",
                "[none]",
            ],
            "origin_time": [*map(wrap, [6, 5, 2, 1, 6, 2])],
        }
    )

    for phylogeny_df_ in (
        phylogeny_df,
        alifestd_assign_contiguous_ids(phylogeny_df),
        alifestd_try_add_ancestor_id_col(phylogeny_df),
        alifestd_try_add_ancestor_id_col(
            alifestd_assign_contiguous_ids(phylogeny_df)
        ),
    ):
        for df in phylogeny_df_, phylogeny_df_.sample(frac=1):
            assert alifestd_find_chronological_inconsistency(df) is None
            df_ = df.copy()
            corrected = alifestd_coerce_chronological_consistency(df)
            assert corrected.reset_index(drop=True).equals(
                df_.reset_index(drop=True),
            )
            assert df.equals(df_)


@pytest.mark.parametrize("wrap", [int, str, float, lambda x: (x,), dt_epoch])
def test_is_chronologically_unordered_asexual1(wrap: typing.Callable):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 22, 333, 44, 5],
            "ancestor_list": [
                "[333]",
                "[333]",
                "[333]",
                "[none]",
                "[333]",
                "[0]",
            ],
            "origin_time": [*map(wrap, [5, 5, 2, 1, 2, 4])],
        }
    )

    for phylogeny_df_ in (
        phylogeny_df,
        alifestd_assign_contiguous_ids(phylogeny_df),
        alifestd_try_add_ancestor_id_col(phylogeny_df),
        alifestd_try_add_ancestor_id_col(
            alifestd_assign_contiguous_ids(phylogeny_df)
        ),
    ):
        for df in phylogeny_df_, phylogeny_df_.sample(frac=1):
            assert alifestd_find_chronological_inconsistency(df) is not None
            df_ = df.copy()
            corrected = alifestd_coerce_chronological_consistency(df)
            assert not corrected.equals(df_)
            assert alifestd_find_chronological_inconsistency(corrected) is None
            assert df.equals(df_)


@pytest.mark.parametrize("wrap", [int, str, float, lambda x: (x,), dt_epoch])
def test_is_chronologically_unordered_asexual2(wrap: typing.Callable):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 22, 333, 44, 5],
            "ancestor_list": [
                "[44]",
                "[0]",
                "[333]",
                "[none]",
                "[333]",
                "[none]",
            ],
            "origin_time": [*map(wrap, [1, 5, 2, 1, 2, 2])],
        }
    )

    for phylogeny_df_ in (
        phylogeny_df,
        alifestd_assign_contiguous_ids(phylogeny_df),
        alifestd_try_add_ancestor_id_col(phylogeny_df),
        alifestd_try_add_ancestor_id_col(
            alifestd_assign_contiguous_ids(phylogeny_df)
        ),
    ):
        for df in phylogeny_df_, phylogeny_df_.sample(frac=1):
            assert alifestd_find_chronological_inconsistency(df) is not None
            df_ = df.copy()
            corrected = alifestd_coerce_chronological_consistency(df)
            assert not corrected.equals(df_)
            assert alifestd_find_chronological_inconsistency(corrected) is None
            assert df.equals(df_)


@pytest.mark.parametrize("wrap", [int, str, float, lambda x: (x,), dt_epoch])
def test_is_chronologically_unordered_asexual3(wrap: typing.Callable):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 22, 333, 44, 5],
            "ancestor_list": [
                "[333]",
                "[5]",
                "[44]",
                "[none]",
                "[333]",
                "[none]",
            ],
            "origin_time": [*map(wrap, [1, 5, 2, 3, 2, 2])],
        }
    )

    for phylogeny_df_ in (
        phylogeny_df,
        alifestd_assign_contiguous_ids(phylogeny_df),
        alifestd_try_add_ancestor_id_col(phylogeny_df),
        alifestd_try_add_ancestor_id_col(
            alifestd_assign_contiguous_ids(phylogeny_df)
        ),
    ):
        for df in phylogeny_df_, phylogeny_df_.sample(frac=1):
            assert alifestd_find_chronological_inconsistency(df) is not None
            df_ = df.copy()
            corrected = alifestd_coerce_chronological_consistency(df)
            assert not corrected.equals(df_)
            assert alifestd_find_chronological_inconsistency(corrected) is None
            assert df.equals(df_)
