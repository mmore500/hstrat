import numpy as np
import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_calc_clade_lookback_n_asexual,
    alifestd_make_empty,
)


def test_empty():
    mt = alifestd_make_empty()
    mt["ancestor_list"] = None
    res = alifestd_calc_clade_lookback_n_asexual(
        mt,
        lookback_n=1,
    )
    assert isinstance(res, np.ndarray)
    assert res.size == 0


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize(
    "lookback_n, expected",
    [
        (0, [0, 1, 2]),
        (1, [0, 0, 1]),
        (2, [0, 0, 0]),
    ],
)
def test_simple1(mutate: bool, lookback_n: int, expected: list):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
        }
    )
    original_df = phylogeny_df.copy()
    result = alifestd_calc_clade_lookback_n_asexual(
        phylogeny_df,
        lookback_n=lookback_n,
        mutate=mutate,
    )
    assert isinstance(result, np.ndarray)
    assert result.tolist() == expected
    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize(
    "lookback_n, expected",
    [
        (0, [1, 0, 2, 3]),
        (1, [0, 0, 0, 1]),
        (2, [0, 0, 0, 0]),
    ],
)
def test_simple2(mutate: bool, lookback_n: int, expected: list):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3],
            "ancestor_list": ["[0]", "[None]", "[0]", "[1]"],
        }
    )
    original_df = phylogeny_df.copy()
    result = alifestd_calc_clade_lookback_n_asexual(
        phylogeny_df,
        lookback_n=lookback_n,
        mutate=mutate,
    )
    assert isinstance(result, np.ndarray)
    assert result.tolist() == expected
    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize(
    "lookback_n, expected",
    [
        (0, [1, 0, 2, 3]),
        (1, [1, 0, 0, 1]),
        (2, [1, 0, 0, 1]),
    ],
)
def test_simple3(mutate: bool, lookback_n: int, expected: list):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3],
            "ancestor_list": ["[None]", "[None]", "[0]", "[1]"],
        }
    )
    original_df = phylogeny_df.copy()
    result = alifestd_calc_clade_lookback_n_asexual(
        phylogeny_df,
        lookback_n=lookback_n,
        mutate=mutate,
    )
    assert isinstance(result, np.ndarray)
    assert result.tolist() == expected
    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize(
    "lookback_n, expected",
    [
        (0, [1, 0, 2, 3]),
        (1, [0, 0, 0, 1]),
        (1, [0, 0, 0, 1]),
        (2, [0, 0, 0, 0]),
    ],
)
def test_simple4(mutate: bool, lookback_n: int, expected: list):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3],
            "ancestor_list": ["[0]", "[None]", "[0]", "[1]"],
        }
    )
    original_df = phylogeny_df.copy()
    result = alifestd_calc_clade_lookback_n_asexual(
        phylogeny_df,
        lookback_n=lookback_n,
        mutate=mutate,
    )
    assert isinstance(result, np.ndarray)
    assert result.tolist() == expected
    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize(
    "lookback_n, expected",
    [
        (0, [0, 1, 2, 3]),
        (1, [0, 1, 0, 1]),
        (1, [0, 1, 0, 1]),
    ],
)
def test_simple5_sorted(mutate: bool, lookback_n: int, expected: list):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3],
            "ancestor_list": ["[None]", "[None]", "[0]", "[1]"],
        }
    ).sort_values("id")
    original_df = phylogeny_df.copy()
    result = alifestd_calc_clade_lookback_n_asexual(
        phylogeny_df,
        lookback_n=lookback_n,
        mutate=mutate,
    )
    assert isinstance(result, np.ndarray)
    assert result.tolist() == expected
    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize(
    "lookback_n, expected",
    [
        (0, [0, 1, 2, 3]),
        (1, [0, 0, 0, 1]),
        (2, [0, 0, 0, 0]),
    ],
)
def test_simple6_sorted(mutate: bool, lookback_n: int, expected: list):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3],
            "ancestor_list": ["[0]", "[None]", "[0]", "[1]"],
        }
    ).sort_values("id")
    original_df = phylogeny_df.copy()
    result = alifestd_calc_clade_lookback_n_asexual(
        phylogeny_df,
        lookback_n=lookback_n,
        mutate=mutate,
    )
    assert isinstance(result, np.ndarray)
    assert result.tolist() == expected
    if not mutate:
        assert original_df.equals(phylogeny_df)
