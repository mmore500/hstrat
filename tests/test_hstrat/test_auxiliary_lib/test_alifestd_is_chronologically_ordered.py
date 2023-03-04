import pandas as pd

from hstrat._auxiliary_lib import (
    alifestd_assign_contiguous_ids,
    alifestd_is_chronologically_ordered,
    alifestd_make_empty,
    alifestd_try_add_ancestor_id_col,
)


def test_is_chronologically_ordered_empty():
    df = alifestd_make_empty()
    df["origin_time"] = []
    assert alifestd_is_chronologically_ordered(df)


def test_is_chronologically_ordered_sexual1():
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
            "origin_time": [5, 5, 2, 1, 2, 0],
        }
    )

    for phylogeny_df_ in phylogeny_df, alifestd_assign_contiguous_ids(
        phylogeny_df
    ):
        for df in phylogeny_df_, phylogeny_df_.sample(frac=1):
            df_ = df.copy()
            assert alifestd_is_chronologically_ordered(df)
            assert alifestd_is_chronologically_ordered(
                df.astype({"origin_time": float})
            )
            assert df.equals(df_)


def test_is_chronologically_ordered_sexual2():
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
            "origin_time": [5, 5, 2, 1, 2, 2],
        }
    )

    for phylogeny_df_ in phylogeny_df, alifestd_assign_contiguous_ids(
        phylogeny_df
    ):
        for df in phylogeny_df_, phylogeny_df_.sample(frac=1):
            df_ = df.copy()
            assert alifestd_is_chronologically_ordered(
                df.astype({"origin_time": float})
            )
            assert df.equals(df_)


def test_is_chronologically_unordered_sexual1():
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
            "origin_time": [5, 5, 2, 1, 2, 6],
        }
    )

    for phylogeny_df_ in phylogeny_df, alifestd_assign_contiguous_ids(
        phylogeny_df
    ):
        for df in phylogeny_df_, phylogeny_df_.sample(frac=1):
            df_ = df.copy()
            assert not alifestd_is_chronologically_ordered(df)
            assert not alifestd_is_chronologically_ordered(
                df.astype({"origin_time": float})
            )
            assert df.equals(df_)


def test_is_chronologically_unordered_sexual2():
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
            "origin_time": [1, 5, 2, 1, 2, 2],
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
            assert not alifestd_is_chronologically_ordered(df)
            assert not alifestd_is_chronologically_ordered(
                df.astype({"origin_time": float})
            )
            assert df.equals(df_)


def test_is_chronologically_unordered_sexual3():
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
            "origin_time": [1, 5, 2, 3, 2, 2],
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
            assert not alifestd_is_chronologically_ordered(df)
            assert not alifestd_is_chronologically_ordered(
                df.astype({"origin_time": float})
            )
            assert df.equals(df_)


def test_is_chronologically_ordered_asexual1():
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
            "origin_time": [6, 5, 2, 1, 6, 2],
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
            assert alifestd_is_chronologically_ordered(df)
            assert alifestd_is_chronologically_ordered(
                df.astype({"origin_time": float})
            )
            assert df.equals(df_)


def test_is_chronologically_ordered_asexual2():
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
            "origin_time": [6, 5, 2, 1, 6, 2],
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
            assert alifestd_is_chronologically_ordered(
                df.astype({"origin_time": float})
            )
            assert df.equals(df_)


def test_is_chronologically_unordered_asexual1():
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
            "origin_time": [5, 5, 2, 1, 2, 4],
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
            assert not alifestd_is_chronologically_ordered(df)
            assert not alifestd_is_chronologically_ordered(
                df.astype({"origin_time": float})
            )
            assert df.equals(df_)


def test_is_chronologically_unordered_asexual2():
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
            "origin_time": [1, 5, 2, 1, 2, 2],
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
            assert not alifestd_is_chronologically_ordered(df)
            assert not alifestd_is_chronologically_ordered(
                df.astype({"origin_time": float})
            )
            assert df.equals(df_)


def test_is_chronologically_unordered_asexual3():
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
            "origin_time": [1, 5, 2, 3, 2, 2],
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
            assert not alifestd_is_chronologically_ordered(df)
            assert not alifestd_is_chronologically_ordered(
                df.astype({"origin_time": float})
            )
            assert df.equals(df_)
