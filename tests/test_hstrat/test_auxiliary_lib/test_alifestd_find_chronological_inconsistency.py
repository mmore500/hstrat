from datetime import datetime, timezone
import typing

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_assign_contiguous_ids,
    alifestd_find_chronological_inconsistency,
    alifestd_make_empty,
    alifestd_parse_ancestor_ids,
    alifestd_try_add_ancestor_id_col,
)


# see https://blog.miguelgrinberg.com/post/it-s-time-for-a-change-datetime-utcnow-is-now-deprecated
def dt_epoch(ts: int) -> datetime:
    return datetime.fromtimestamp(ts, tz=timezone.utc).replace(tzinfo=None)


def _is_chronological_inconsistency(
    df: pd.DataFrame, id_: typing.Optional[int]
) -> bool:
    if id_ is None:
        return False
    ancestor_list_str = df.loc[df["id"] == id_, "ancestor_list"].iloc[0]
    ancestor_ids = alifestd_parse_ancestor_ids(ancestor_list_str)

    if not ancestor_ids:
        return False

    for parent_id in ancestor_ids:
        parent_origin_time = df.loc[df["id"] == parent_id, "origin_time"].iloc[
            0
        ]
        if parent_origin_time > df.loc[df["id"] == id_, "origin_time"].iloc[0]:
            return True

    return False


@pytest.mark.parametrize("dtype", ["int", "str", "float", "object"])
def test_find_chronological_inconsistency_empty(dtype: str):
    df = alifestd_make_empty()
    df["origin_time"] = pd.Series(dtype=dtype)
    assert alifestd_find_chronological_inconsistency(df) is None


def test_find_chronological_inconsistency_empty_datetime():
    df = alifestd_make_empty()
    df["origin_time"] = pd.to_datetime(pd.Series())
    assert alifestd_find_chronological_inconsistency(df) is None


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
            df_ = df.copy()
            assert alifestd_find_chronological_inconsistency(df) is None
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
            df_ = df.copy()
            assert alifestd_find_chronological_inconsistency(df) is None
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
            df_ = df.copy()
            assert _is_chronological_inconsistency(
                df_,
                alifestd_find_chronological_inconsistency(df),
            )
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
            df_ = df.copy()
            assert _is_chronological_inconsistency(
                df_,
                alifestd_find_chronological_inconsistency(df),
            )
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
            df_ = df.copy()
            assert _is_chronological_inconsistency(
                df_,
                alifestd_find_chronological_inconsistency(df),
            )
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
            df_ = df.copy()
            assert alifestd_find_chronological_inconsistency(df) is None
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
            df_ = df.copy()
            assert alifestd_find_chronological_inconsistency(df) is None
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
            df_ = df.copy()
            assert _is_chronological_inconsistency(
                df_,
                alifestd_find_chronological_inconsistency(df),
            )
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
            df_ = df.copy()
            assert _is_chronological_inconsistency(
                df_,
                alifestd_find_chronological_inconsistency(df),
            )
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
            df_ = df.copy()
            assert _is_chronological_inconsistency(
                df_,
                alifestd_find_chronological_inconsistency(df),
            )
            assert df.equals(df_)
