import os

import opytional as opyt
import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_make_ancestor_id_col,
    alifestd_parse_ancestor_id,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny-empty-list-notation.csv"
        ),
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_alifestd_make_ancestor_id_col(phylogeny_df):

    phylogeny_df["ancestor_id"] = alifestd_make_ancestor_id_col(
        phylogeny_df["id"], phylogeny_df["ancestor_list"]
    )
    assert all(
        (
            ancestor_id
            == opyt.or_value(alifestd_parse_ancestor_id(ancestor_list), id_)
            for id_, ancestor_id, ancestor_list in zip(
                phylogeny_df["id"],
                phylogeny_df["ancestor_id"],
                phylogeny_df["ancestor_list"],
            )
        )
    )


def test_alifestd_make_ancestor_id_col_empty():
    res = alifestd_make_ancestor_id_col(
        pd.Series(dtype=int), pd.Series(dtype=str)
    )
    assert len(res) == 0
    assert pd.api.types.is_integer_dtype(res.dtype)
