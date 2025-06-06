import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_make_empty,
    alifestd_mark_clade_faithpd_asexual,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def test_empty():
    mt = alifestd_make_empty()
    mt["origin_time"] = None
    res = alifestd_mark_clade_faithpd_asexual(mt)
    assert "clade_faithpd" in res
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
    result_df = alifestd_mark_clade_faithpd_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    # align by id for assertions
    result_df.index = result_df["id"]
    assert result_df.loc[0, "clade_faithpd"] == 30
    assert result_df.loc[1, "clade_faithpd"] == 20
    assert result_df.loc[2, "clade_faithpd"] == 0

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
    result_df = alifestd_mark_clade_faithpd_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[1, "clade_faithpd"] == 25
    assert result_df.loc[0, "clade_faithpd"] == 55
    assert result_df.loc[2, "clade_faithpd"] == 0
    assert result_df.loc[3, "clade_faithpd"] == 0

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
    result_df = alifestd_mark_clade_faithpd_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[1, "clade_faithpd"] == 25
    assert result_df.loc[0, "clade_faithpd"] == 20
    assert result_df.loc[2, "clade_faithpd"] == 0
    assert result_df.loc[3, "clade_faithpd"] == 0

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple4(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3],
            "ancestor_list": ["[0]", "[None]", "[0]", "[1]"],
            "origin_time": [20, 10, 30, 45],
        }
    ).sort_values("id")
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_clade_faithpd_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[1, "clade_faithpd"] == 25
    assert result_df.loc[0, "clade_faithpd"] == 55
    assert result_df.loc[2, "clade_faithpd"] == 0
    assert result_df.loc[3, "clade_faithpd"] == 0

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple5(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3],
            "ancestor_list": ["[None]", "[None]", "[0]", "[1]"],
            "origin_time": [20, 10, 30, 45],
        }
    ).sort_values("id")
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_clade_faithpd_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[1, "clade_faithpd"] == 25
    assert result_df.loc[0, "clade_faithpd"] == 20
    assert result_df.loc[2, "clade_faithpd"] == 0
    assert result_df.loc[3, "clade_faithpd"] == 0

    if not mutate:
        assert original_df.equals(phylogeny_df)
