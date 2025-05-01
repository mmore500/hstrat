import numpy as np
import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_make_empty,
    alifestd_mask_monomorphic_clades_asexual,
)


def test_empty():
    mt = alifestd_make_empty()
    result_df = alifestd_mask_monomorphic_clades_asexual(
        mt,
        trait_mask=np.array([], dtype=bool),
        trait_values=np.array([], dtype=int),
    )
    assert "alifestd_mask_monomorphic_clades_asexual" in result_df.columns
    assert len(result_df) == 0


# Test simple cases with separate parametrization for mutate and dtype
@pytest.mark.parametrize("mutate", [False, True])
@pytest.mark.parametrize("dtype", [int, float, str, tuple])
def test_simple1(mutate: bool, dtype: type):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[0]"],
            "origin_time": [0, 10, 30],
        }
    )
    original_df = phylogeny_df.copy()
    trait_mask = np.array([False, True, False], dtype=bool)
    raw_traits = [0, 1, 2]
    trait_values = np.array(raw_traits, dtype=dtype)

    result_df = alifestd_mask_monomorphic_clades_asexual(
        phylogeny_df,
        mutate=mutate,
        trait_mask=trait_mask,
        trait_values=trait_values,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[0, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[1, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[2, "alifestd_mask_monomorphic_clades_asexual"]
    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [False, True])
@pytest.mark.parametrize("dtype", [int, float, str, tuple])
def test_simple2(mutate: bool, dtype: type):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3],
            "ancestor_list": ["[0]", "[None]", "[0]", "[1]"],
            "origin_time": [20, 10, 30, 45],
        }
    )
    original_df = phylogeny_df.copy()
    trait_mask = np.array([True, False, True, False], dtype=bool)
    raw_traits = [5, 6, 7, 5]
    trait_values = np.array(raw_traits, dtype=dtype)

    result_df = alifestd_mask_monomorphic_clades_asexual(
        phylogeny_df,
        mutate=mutate,
        trait_mask=trait_mask,
        trait_values=trait_values,
    )
    result_df.index = result_df["id"]
    assert not result_df.loc[0, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[1, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[2, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[3, "alifestd_mask_monomorphic_clades_asexual"]
    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [False, True])
@pytest.mark.parametrize("dtype", [int, float, str, tuple])
def test_simple3(mutate: bool, dtype: type):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 4],
            "ancestor_list": ["[None]", "[None]", "[0]", "[1]"],
            "origin_time": [20, 10, 30, 45],
        }
    )
    original_df = phylogeny_df.copy()
    trait_mask = np.array([True, False, True, False], dtype=bool)
    raw_traits = [3, 3, 3, 5]
    trait_values = np.array(raw_traits, dtype=dtype)

    result_df = alifestd_mask_monomorphic_clades_asexual(
        phylogeny_df,
        mutate=mutate,
        trait_mask=trait_mask,
        trait_values=trait_values,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[0, "alifestd_mask_monomorphic_clades_asexual"]
    assert not result_df.loc[1, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[2, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[4, "alifestd_mask_monomorphic_clades_asexual"]
    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [False, True])
@pytest.mark.parametrize("dtype", [int, float, str, tuple])
def test_simple4(mutate: bool, dtype: type):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_list": ["[None]", "[0]", "[0]", "[0]"],
        }
    )
    original_df = phylogeny_df.copy()
    trait_mask = np.array([True, True, True, True], dtype=bool)
    raw_traits = [9, 7, 7, 7]
    trait_values = np.array(raw_traits, dtype=dtype)

    result_df = alifestd_mask_monomorphic_clades_asexual(
        phylogeny_df,
        mutate=mutate,
        trait_mask=trait_mask,
        trait_values=trait_values,
    )
    result_df.index = result_df["id"]
    assert not result_df.loc[0, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[1, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[2, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[3, "alifestd_mask_monomorphic_clades_asexual"]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [False, True])
@pytest.mark.parametrize("dtype", [int, float, str, tuple])
def test_simple5(mutate: bool, dtype: type):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3, 4],
            "ancestor_list": ["[0]", "[None]", "[0]", "[1]", "[1]"],
        }
    )
    original_df = phylogeny_df.copy()
    trait_mask = np.array([True, False, False, True, False], dtype=bool)
    raw_traits = [1, 2, 3, 1, 4]
    trait_values = np.array(raw_traits, dtype=dtype)

    result_df = alifestd_mask_monomorphic_clades_asexual(
        phylogeny_df,
        mutate=mutate,
        trait_mask=trait_mask,
        trait_values=trait_values,
    )
    result_df.index = result_df["id"]
    assert not result_df.loc[1, "alifestd_mask_monomorphic_clades_asexual"]
    assert not result_df.loc[0, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[2, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[3, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[4, "alifestd_mask_monomorphic_clades_asexual"]
    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [False, True])
@pytest.mark.parametrize("dtype", [int, float, str, tuple])
def test_simple6(mutate: bool, dtype: type):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0],
            "ancestor_list": ["[None]", "[None]"],
        }
    )
    original_df = phylogeny_df.copy()
    trait_mask = np.array([False, True], dtype=bool)
    raw_traits = [8, 9]
    trait_values = np.array(raw_traits, dtype=dtype)

    result_df = alifestd_mask_monomorphic_clades_asexual(
        phylogeny_df,
        mutate=mutate,
        trait_mask=trait_mask,
        trait_values=trait_values,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[1, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[0, "alifestd_mask_monomorphic_clades_asexual"]
    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [False, True])
@pytest.mark.parametrize("dtype", [int, float, str, tuple])
def test_simple7(mutate: bool, dtype: type):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
            "origin_time": [0, 10, 30],
        }
    )
    original_df = phylogeny_df.copy()
    trait_mask = np.array([False, True, True], dtype=bool)
    raw_traits = [5, 6, 6]
    trait_values = np.array(raw_traits, dtype=dtype)

    result_df = alifestd_mask_monomorphic_clades_asexual(
        phylogeny_df,
        mutate=mutate,
        trait_mask=trait_mask,
        trait_values=trait_values,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[0, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[1, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[2, "alifestd_mask_monomorphic_clades_asexual"]
    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [False, True])
@pytest.mark.parametrize("dtype", [int, float, str, tuple])
def test_simple8(mutate: bool, dtype: type):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[0]"],
            "origin_time": [0, 10, 30],
        }
    )
    original_df = phylogeny_df.copy()
    trait_mask = np.array([False, False, False], dtype=bool)
    raw_traits = [9, 8, 7]
    trait_values = np.array(raw_traits, dtype=dtype)

    result_df = alifestd_mask_monomorphic_clades_asexual(
        phylogeny_df,
        mutate=mutate,
        trait_mask=trait_mask,
        trait_values=trait_values,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[0, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[1, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[2, "alifestd_mask_monomorphic_clades_asexual"]
    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [False, True])
@pytest.mark.parametrize("dtype", [int, float, str, tuple])
def test_simple9(mutate: bool, dtype: type):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_list": ["[None]", "[0]", "[0]", "[0]"],
        }
    )
    original_df = phylogeny_df.copy()
    trait_mask = np.array([False, True, True, True], dtype=bool)
    raw_traits = [9, 7, 7, 7]
    trait_values = np.array(raw_traits, dtype=dtype)

    result_df = alifestd_mask_monomorphic_clades_asexual(
        phylogeny_df,
        mutate=mutate,
        trait_mask=trait_mask,
        trait_values=trait_values,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[0, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[1, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[2, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[3, "alifestd_mask_monomorphic_clades_asexual"]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [False, True])
@pytest.mark.parametrize("dtype", [int, float, str, tuple])
def test_simple10(mutate: bool, dtype: type):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_list": ["[None]", "[0]", "[0]", "[0]"],
        }
    )
    original_df = phylogeny_df.copy()
    trait_mask = np.array([False, True, True, True], dtype=bool)
    raw_traits = [9, 7, 7, 8]
    trait_values = np.array(raw_traits, dtype=dtype)

    result_df = alifestd_mask_monomorphic_clades_asexual(
        phylogeny_df,
        mutate=mutate,
        trait_mask=trait_mask,
        trait_values=trait_values,
    )
    result_df.index = result_df["id"]
    assert not result_df.loc[0, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[1, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[2, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[3, "alifestd_mask_monomorphic_clades_asexual"]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [False, True])
@pytest.mark.parametrize("dtype", [int, float, str, tuple])
def test_simple11(mutate: bool, dtype: type):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[0]"],
            "origin_time": [0, 10, 30],
        }
    )
    original_df = phylogeny_df.copy()
    trait_mask = np.array([False, True, True], dtype=bool)
    raw_traits = [9, 8, 7]
    trait_values = np.array(raw_traits, dtype=dtype)

    result_df = alifestd_mask_monomorphic_clades_asexual(
        phylogeny_df,
        mutate=mutate,
        trait_mask=trait_mask,
        trait_values=trait_values,
    )
    result_df.index = result_df["id"]
    assert not result_df.loc[0, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[1, "alifestd_mask_monomorphic_clades_asexual"]
    assert result_df.loc[2, "alifestd_mask_monomorphic_clades_asexual"]
    if not mutate:
        assert original_df.equals(phylogeny_df)
