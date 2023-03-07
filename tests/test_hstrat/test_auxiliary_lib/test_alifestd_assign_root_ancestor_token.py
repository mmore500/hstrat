import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_assign_root_ancestor_token,
    alifestd_find_root_ids,
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
@pytest.mark.parametrize(
    "root_ancestor_token",
    [
        "",
        "None",
        "none",
    ],
)
def test_alifestd_assign_root_ancestor_token(
    phylogeny_df, apply, root_ancestor_token
):
    phylogeny_df = apply(phylogeny_df)
    phylogeny_df_ = phylogeny_df.copy()
    res_df = alifestd_assign_root_ancestor_token(
        phylogeny_df, root_ancestor_token
    )
    assert alifestd_validate(res_df)
    assert sorted(
        res_df[res_df["ancestor_list"] == f"[{root_ancestor_token}]"]["id"]
    ) == sorted(alifestd_find_root_ids(phylogeny_df_))
    assert phylogeny_df.equals(phylogeny_df_)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-sexual-phylogeny.csv"
        ),
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
@pytest.mark.parametrize(
    "root_ancestor_token",
    [
        "",
        "None",
        "none",
    ],
)
def test_alifestd_assign_root_ancestor_token_mutate(
    phylogeny_df, apply, root_ancestor_token
):
    phylogeny_df = apply(phylogeny_df)
    phylogeny_df_ = phylogeny_df.copy()
    res_df = alifestd_assign_root_ancestor_token(
        phylogeny_df, root_ancestor_token, mutate=True
    )
    assert alifestd_validate(res_df)
    assert sorted(
        res_df[res_df["ancestor_list"] == f"[{root_ancestor_token}]"]["id"]
    ) == sorted(alifestd_find_root_ids(phylogeny_df_))
