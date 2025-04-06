import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_make_empty,
    alifestd_mark_is_left_child_asexual,
)


def test_empty():
    mt = alifestd_make_empty()
    res = alifestd_mark_is_left_child_asexual(mt)
    assert "left_child" in res
    assert len(res) == 0


@pytest.mark.parametrize("mutate", [True, False])
def test_simple1(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[0]"],
            "origin_time": [0, 10, 30],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_is_left_child_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    assert not result_df.loc[0, "is_left_child"]
    assert result_df.loc[1, "is_left_child"]
    assert not result_df.loc[2, "is_left_child"]

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
    with pytest.raises(ValueError):
        alifestd_mark_is_left_child_asexual(
            phylogeny_df,
            mutate=mutate,
        )

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple3(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 4],
            "ancestor_list": ["[None]", "[None]", "[0]", "[1]"],
            "origin_time": [20, 10, 30, 45],
        }
    )
    original_df = phylogeny_df.copy()
    with pytest.raises(ValueError):
        alifestd_mark_is_left_child_asexual(
            phylogeny_df,
            mutate=mutate,
        )

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple4(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[0]"],
            "origin_time": [0, 10, 30],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_is_left_child_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    assert not result_df.loc[0, "is_left_child"]
    assert result_df.loc[1, "is_left_child"]
    assert not result_df.loc[2, "is_left_child"]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple5(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3, 4],
            "ancestor_list": ["[0]", "[None]", "[0]", "[1]", "[1]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_is_left_child_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[1, "is_left_child"]
    assert not result_df.loc[0, "is_left_child"]
    assert not result_df.loc[2, "is_left_child"]
    assert result_df.loc[3, "is_left_child"]
    assert not result_df.loc[4, "is_left_child"]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple6(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0],
            "ancestor_list": ["[None]", "[None]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_is_left_child_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert not result_df.loc[1, "is_left_child"]
    assert not result_df.loc[0, "is_left_child"]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple7(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
            "origin_time": [0, 10, 30],
        }
    )
    original_df = phylogeny_df.copy()
    with pytest.raises(ValueError):
        alifestd_mark_is_left_child_asexual(
            phylogeny_df,
            mutate=mutate,
        )

    if not mutate:
        assert original_df.equals(phylogeny_df)
