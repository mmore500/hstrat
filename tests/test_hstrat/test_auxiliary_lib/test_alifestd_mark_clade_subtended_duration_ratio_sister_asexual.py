import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_make_empty,
    alifestd_mark_clade_subtended_duration_ratio_sister_asexual,
)


def test_empty():
    mt = alifestd_make_empty()
    mt["origin_time"] = None
    res = alifestd_mark_clade_subtended_duration_ratio_sister_asexual(mt)
    assert "clade_subtended_duration_ratio_sister" in res
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
    with pytest.raises(ValueError):
        alifestd_mark_clade_subtended_duration_ratio_sister_asexual(
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
    with pytest.raises(ValueError):
        alifestd_mark_clade_subtended_duration_ratio_sister_asexual(
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
        alifestd_mark_clade_subtended_duration_ratio_sister_asexual(
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
            "origin_time": [5, 10, 30],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_clade_subtended_duration_ratio_sister_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    assert result_df.loc[0, "clade_subtended_duration_ratio_sister"] == 1
    assert result_df.loc[1, "clade_subtended_duration_ratio_sister"] == 5 / 25
    assert result_df.loc[2, "clade_subtended_duration_ratio_sister"] == 25 / 5

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple5(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3, 4, 5, 7],
            "ancestor_id": [0, 0, 0, 1, 1, 2, 2],
            "origin_time": [10, 5, 30, 20, 40, 50, 65],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_clade_subtended_duration_ratio_sister_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    assert result_df.loc[0, "clade_subtended_duration_ratio_sister"] == 1
    assert result_df.loc[
        1, "clade_subtended_duration_ratio_sister"
    ] == pytest.approx(35 / 60)
    assert result_df.loc[
        2, "clade_subtended_duration_ratio_sister"
    ] == pytest.approx(60 / 35)
    assert result_df.loc[
        3, "clade_subtended_duration_ratio_sister"
    ] == pytest.approx(10 / 30)
    assert result_df.loc[
        4, "clade_subtended_duration_ratio_sister"
    ] == pytest.approx(30 / 10)
    assert result_df.loc[
        5, "clade_subtended_duration_ratio_sister"
    ] == pytest.approx(20 / 35)
    assert result_df.loc[
        7, "clade_subtended_duration_ratio_sister"
    ] == pytest.approx(35 / 20)

    if not mutate:
        assert original_df.equals(phylogeny_df)
