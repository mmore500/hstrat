import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_chronological_sort,
    alifestd_is_chronologically_sorted,
    alifestd_make_empty,
)


def test_chronological_sort_empty():
    df = alifestd_make_empty()
    df["origin_time"] = []
    df = alifestd_chronological_sort(df)
    assert alifestd_is_chronologically_sorted(df)


@pytest.mark.parametrize("mutate", [True, False])
def test_chronological_sort(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 22, 333, 44, 5],
            "origin_time": [0, 1, 2, 2, 6, 5],
        }
    )
    original_df = phylogeny_df.copy()
    expected_result_df = pd.DataFrame(
        {
            "id": [0, 1, 22, 333, 5, 44],
            "origin_time": [0, 1, 2, 2, 5, 6],
        }
    )
    result_df = alifestd_chronological_sort(phylogeny_df, mutate=mutate)

    assert alifestd_is_chronologically_sorted(result_df)
    assert expected_result_df.equals(result_df)

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_chronological_sort_nop(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 22, 333, 44, 5],
            "origin_time": [0, 1, 2, 2, 5, 6],
        }
    )
    original_df = phylogeny_df.copy()
    expected_result_df = original_df
    result_df = alifestd_chronological_sort(phylogeny_df, mutate=mutate)

    assert alifestd_is_chronologically_sorted(result_df)
    assert expected_result_df.equals(result_df)

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize("how", ["origin_time", "destruction_time"])
def test_chronological_sort_how(mutate: bool, how: str):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 22, 333, 44, 5],
            how: [0, 1, 2, 2, 6, 5],
        }
    )
    original_df = phylogeny_df.copy()
    expected_result_df = pd.DataFrame(
        {
            "id": [0, 1, 22, 333, 5, 44],
            how: [0, 1, 2, 2, 5, 6],
        }
    )
    result_df = alifestd_chronological_sort(
        phylogeny_df, how=how, mutate=mutate
    )

    assert alifestd_is_chronologically_sorted(result_df, how=how)
    assert expected_result_df.equals(result_df)

    if not mutate:
        assert original_df.equals(phylogeny_df)
