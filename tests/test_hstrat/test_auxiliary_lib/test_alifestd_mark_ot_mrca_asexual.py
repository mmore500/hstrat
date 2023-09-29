import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_is_chronologically_ordered,
    alifestd_make_empty,
    alifestd_mark_ot_mrca_asexual,
    alifestd_to_working_format,
    alifestd_validate,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
        ),
    ],
)
def test_fuzz(phylogeny_df: pd.DataFrame):
    assert alifestd_is_chronologically_ordered(phylogeny_df)
    original = phylogeny_df.copy()

    result = alifestd_mark_ot_mrca_asexual(phylogeny_df)

    assert alifestd_validate(result)
    assert alifestd_is_chronologically_ordered(result)
    assert original.equals(phylogeny_df)

    assert all(original["id"].min() <= result["ot_mrca_id"])
    assert all(result["ot_mrca_id"] <= original["id"].max())

    assert all(original["origin_time"].min() <= result["ot_mrca_time_of"])
    assert all(result["ot_mrca_time_of"] <= original["origin_time"].max())

    assert all(0 <= result["ot_mrca_time_since"])
    assert all(result["ot_mrca_time_since"] <= original["origin_time"].max())


def test_empty():
    mt = alifestd_make_empty()
    mt["origin_time"] = None
    res = alifestd_mark_ot_mrca_asexual(mt)
    assert "ot_mrca_id" in res
    assert "ot_mrca_time_of" in res
    assert "ot_mrca_time_since" in res
    assert len(res) == 0


@pytest.mark.parametrize("mutate", [True, False])
def test_simple1(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "origin_time": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_ot_mrca_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    assert result_df.loc[0, "ot_mrca_id"] == 0
    assert result_df.loc[1, "ot_mrca_id"] == 1
    assert result_df.loc[2, "ot_mrca_id"] == 2

    assert result_df.loc[0, "ot_mrca_time_of"] == 0
    assert result_df.loc[1, "ot_mrca_time_of"] == 1
    assert result_df.loc[2, "ot_mrca_time_of"] == 2

    assert result_df.loc[0, "ot_mrca_time_since"] == 0
    assert result_df.loc[1, "ot_mrca_time_since"] == 0
    assert result_df.loc[2, "ot_mrca_time_since"] == 0

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple2(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 3, 2],
            "origin_time": [1, 0, 2, 3],
            "ancestor_list": ["[0]", "[None]", "[0]", "[3]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_ot_mrca_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    assert result_df.loc[0, "ot_mrca_id"] == 0
    assert result_df.loc[1, "ot_mrca_id"] == 0
    assert result_df.loc[3, "ot_mrca_id"] == 3
    assert result_df.loc[2, "ot_mrca_id"] == 2

    assert result_df.loc[0, "ot_mrca_time_of"] == 0
    assert result_df.loc[1, "ot_mrca_time_of"] == 0
    assert result_df.loc[3, "ot_mrca_time_of"] == 2
    assert result_df.loc[2, "ot_mrca_time_of"] == 3

    assert result_df.loc[0, "ot_mrca_time_since"] == 0
    assert result_df.loc[1, "ot_mrca_time_since"] == 1
    assert result_df.loc[3, "ot_mrca_time_since"] == 0
    assert result_df.loc[2, "ot_mrca_time_since"] == 0

    if not mutate:
        assert original_df.equals(phylogeny_df)
