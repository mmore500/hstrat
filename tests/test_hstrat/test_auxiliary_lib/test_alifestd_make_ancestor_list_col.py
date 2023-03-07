import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_make_ancestor_id_col,
    alifestd_make_ancestor_list_col,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


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
def test_alifestd_make_ancestor_list_col(phylogeny_df):

    phylogeny_df["ancestor_id"] = alifestd_make_ancestor_id_col(
        phylogeny_df["id"], phylogeny_df["ancestor_list"]
    )
    assert all(
        alifestd_make_ancestor_list_col(
            phylogeny_df["id"], phylogeny_df["ancestor_id"]
        ).str.lower()
        == phylogeny_df["ancestor_list"].str.lower()
    )


def test_alifestd_make_ancestor_list_col_empty():
    res = alifestd_make_ancestor_list_col(
        pd.Series(dtype=int), pd.Series(dtype=int)
    )
    assert len(res) == 0
    assert pd.api.types.is_string_dtype(res.dtype)


def test_alifestd_make_ancestor_list_col_root_ancestor_token():
    res = alifestd_make_ancestor_list_col(
        pd.Series([0]),
        pd.Series([0]),
        root_ancestor_token="boop",
    )
    assert len(res) == 1
    pd.testing.assert_series_equal(
        res,
        pd.Series("[boop]"),
    )
