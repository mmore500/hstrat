import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_make_empty,
    alifestd_mark_origin_time_delta_asexual,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def test_empty():
    mt = alifestd_make_empty()
    mt["origin_time"] = None
    res = alifestd_mark_origin_time_delta_asexual(mt)
    assert "ancestor_origin_time" in res
    assert "origin_time_delta" in res
    assert len(res) == 0


@pytest.mark.parametrize("mutate", [True, False])
def test_simple1(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
            "origin_time": [0, 10, 30],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_origin_time_delta_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    assert result_df.loc[0, "ancestor_origin_time"] == 0
    assert result_df.loc[1, "ancestor_origin_time"] == 0
    assert result_df.loc[2, "ancestor_origin_time"] == 10
    assert result_df.loc[0, "origin_time_delta"] == 0
    assert result_df.loc[1, "origin_time_delta"] == 10
    assert result_df.loc[2, "origin_time_delta"] == 20

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple2(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3],
            "ancestor_list": ["[0]", "[None]", "[0]", "[1]"],
            "origin_time": [20, 10, 30, 45],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_origin_time_delta_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[1, "ancestor_origin_time"] == 10
    assert result_df.loc[0, "ancestor_origin_time"] == 10
    assert result_df.loc[2, "ancestor_origin_time"] == 10
    assert result_df.loc[3, "ancestor_origin_time"] == 20

    assert result_df.loc[1, "origin_time_delta"] == 10
    assert result_df.loc[0, "origin_time_delta"] == 0
    assert result_df.loc[2, "origin_time_delta"] == 20
    assert result_df.loc[3, "origin_time_delta"] == 25

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple3(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3],
            "ancestor_list": ["[None]", "[None]", "[0]", "[1]"],
            "origin_time": [20, 10, 30, 45],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_origin_time_delta_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[1, "ancestor_origin_time"] == 20
    assert result_df.loc[0, "ancestor_origin_time"] == 10
    assert result_df.loc[2, "ancestor_origin_time"] == 10
    assert result_df.loc[3, "ancestor_origin_time"] == 20
    assert result_df.loc[1, "origin_time_delta"] == 0
    assert result_df.loc[0, "origin_time_delta"] == 0
    assert result_df.loc[2, "origin_time_delta"] == 20
    assert result_df.loc[3, "origin_time_delta"] == 25

    if not mutate:
        assert original_df.equals(phylogeny_df)
