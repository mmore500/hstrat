import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_make_empty,
    alifestd_sum_origin_time_deltas_asexual,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def test_empty():
    mt = alifestd_make_empty()
    mt["origin_time"] = None
    assert 0 == alifestd_sum_origin_time_deltas_asexual(mt)


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
    assert 30 == alifestd_sum_origin_time_deltas_asexual(
        phylogeny_df,
        mutate=mutate,
    )

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
    assert 55 == alifestd_sum_origin_time_deltas_asexual(
        phylogeny_df,
        mutate=mutate,
    )

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
    assert 45 == alifestd_sum_origin_time_deltas_asexual(
        phylogeny_df,
        mutate=mutate,
    )

    if not mutate:
        assert original_df.equals(phylogeny_df)
