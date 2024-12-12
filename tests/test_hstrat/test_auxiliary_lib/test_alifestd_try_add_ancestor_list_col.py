import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_convert_root_ancestor_token,
    alifestd_make_ancestor_list_col,
    alifestd_to_working_format,
    alifestd_try_add_ancestor_id_col,
    alifestd_try_add_ancestor_list_col,
    alifestd_validate,
)

from ._impl import enforce_identical_polars_result

assets_path = os.path.join(os.path.dirname(__file__), "assets")


alifestd_try_add_ancestor_list_col_ = enforce_identical_polars_result(
    alifestd_try_add_ancestor_list_col,
)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
@pytest.mark.parametrize(
    "apply",
    [
        alifestd_to_working_format,
        lambda x: x,
    ],
)
def test_alifestd_try_add_ancestor_id_col_asexual(phylogeny_df, apply):
    phylogeny_df = alifestd_try_add_ancestor_id_col(
        apply(phylogeny_df),
    )
    phylogeny_df["ancestor_list"] = alifestd_convert_root_ancestor_token(
        phylogeny_df["ancestor_list"],
        root_ancestor_token="None",
    )
    phylogeny_df_ = phylogeny_df.copy()

    assert alifestd_validate(phylogeny_df)
    assert (
        phylogeny_df["ancestor_list"]
        == alifestd_make_ancestor_list_col(
            phylogeny_df["id"],
            phylogeny_df["ancestor_id"],
            root_ancestor_token="None",
        )
    ).all(), phylogeny_df
    pd.testing.assert_frame_equal(phylogeny_df_, phylogeny_df)

    res_df = alifestd_try_add_ancestor_list_col_(
        phylogeny_df,
        root_ancestor_token="None",
    )
    assert (
        res_df["ancestor_list"]
        == alifestd_make_ancestor_list_col(
            res_df["id"],
            res_df["ancestor_id"],
            root_ancestor_token="None",
        )
    ).all()
    pd.testing.assert_frame_equal(phylogeny_df_, phylogeny_df)

    res_df = alifestd_try_add_ancestor_list_col_(
        phylogeny_df,
        root_ancestor_token="None",
    )
    assert (
        res_df["ancestor_list"]
        == alifestd_make_ancestor_list_col(
            res_df["id"],
            res_df["ancestor_id"],
            root_ancestor_token="None",
        )
    ).all()

    res_df = alifestd_try_add_ancestor_list_col_(
        phylogeny_df,
        root_ancestor_token="None",
    )
    assert (
        res_df["ancestor_list"]
        == alifestd_make_ancestor_list_col(
            res_df["id"],
            res_df["ancestor_id"],
            root_ancestor_token="None",
        )
    ).all()

    res_df = res_df.copy()
    res_df.drop(columns="ancestor_list", inplace=True)
    assert "ancestor_list" not in res_df
    res_df = alifestd_try_add_ancestor_list_col_(
        res_df,
        root_ancestor_token="None",
    )
    assert (
        res_df["ancestor_list"]
        == alifestd_make_ancestor_list_col(
            res_df["id"],
            res_df["ancestor_id"],
            root_ancestor_token="None",
        )
    ).all()

    phylogeny_df.drop(columns="ancestor_id", inplace=True)
    assert "ancestor_id" not in phylogeny_df
    res_df = alifestd_try_add_ancestor_list_col_(phylogeny_df)
    pd.testing.assert_frame_equal(res_df, phylogeny_df)

    phylogeny_df.drop(columns="ancestor_list", inplace=True)
    assert "ancestor_list" not in phylogeny_df
    res_df = alifestd_try_add_ancestor_list_col_(phylogeny_df)
    pd.testing.assert_frame_equal(res_df, phylogeny_df)
