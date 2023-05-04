import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_make_ancestor_id_col,
    alifestd_to_working_format,
    alifestd_try_add_ancestor_id_col,
    alifestd_validate,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-sexual-phylogeny.csv"
        ),
    ],
)
@pytest.mark.parametrize(
    "apply",
    [
        alifestd_to_working_format,
        alifestd_try_add_ancestor_id_col,
        lambda x: x,
    ],
)
def test_alifestd_try_add_ancestor_id_col_sexual(phylogeny_df, apply):
    phylogeny_df = apply(phylogeny_df)
    phylogeny_df_ = phylogeny_df.copy()
    res_df = alifestd_try_add_ancestor_id_col(phylogeny_df)
    assert "ancestor_id" not in res_df
    assert phylogeny_df.equals(phylogeny_df_)


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
        alifestd_try_add_ancestor_id_col,
        lambda x: x,
    ],
)
def test_alifestd_try_add_ancestor_id_col_asexual(phylogeny_df, apply):
    phylogeny_df = apply(phylogeny_df)
    phylogeny_df_ = phylogeny_df.copy()
    res_df = alifestd_try_add_ancestor_id_col(phylogeny_df)
    assert alifestd_validate(res_df)
    assert "ancestor_id" in res_df
    assert (
        res_df["ancestor_id"]
        == alifestd_make_ancestor_id_col(res_df["id"], res_df["ancestor_list"])
    ).all()
    assert phylogeny_df.equals(phylogeny_df_)
