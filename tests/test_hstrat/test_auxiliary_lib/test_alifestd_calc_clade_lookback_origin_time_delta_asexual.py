import numpy as np
import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_calc_clade_lookback_origin_time_delta_asexual,
    alifestd_make_empty,
)


def test_empty():
    mt = alifestd_make_empty()
    mt["origin_time"] = None
    res = alifestd_calc_clade_lookback_origin_time_delta_asexual(
        mt,
        lookback_origin_time_delta=1.0,
    )
    assert isinstance(res, np.ndarray)
    assert res.size == 0


def test_missing_origin_time():
    df = pd.DataFrame({"id": [0], "ancestor_list": ["[None]"]})
    with pytest.raises(ValueError):
        alifestd_calc_clade_lookback_origin_time_delta_asexual(
            df,
            lookback_origin_time_delta=1.0,
        )


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize(
    "threshold, expected",
    [
        (0.0, [0, 1, 2]),
        (15.0, [0, 0, 1]),
        (100.0, [0, 0, 0]),
    ],
)
def test_simple1(mutate: bool, threshold: float, expected: list):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
            "origin_time": [0, 10, 30],
        }
    )
    original_df = phylogeny_df.copy()
    result = alifestd_calc_clade_lookback_origin_time_delta_asexual(
        phylogeny_df,
        lookback_origin_time_delta=threshold,
        mutate=mutate,
    )
    assert isinstance(result, np.ndarray)
    assert result.tolist() == expected
    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize(
    "threshold, expected",
    [
        (0.0, [1, 0, 2, 3]),
        (25.0, [0, 0, 0, 1]),
        (100.0, [0, 0, 0, 0]),
    ],
)
def test_simple2(mutate: bool, threshold: float, expected: list):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3],
            "ancestor_list": ["[0]", "[None]", "[0]", "[1]"],
            "origin_time": [20, 10, 30, 45],
        }
    )
    original_df = phylogeny_df.copy()
    result = alifestd_calc_clade_lookback_origin_time_delta_asexual(
        phylogeny_df,
        lookback_origin_time_delta=threshold,
        mutate=mutate,
    )
    assert isinstance(result, np.ndarray)
    assert result.tolist() == expected
    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize(
    "threshold, expected",
    [
        (0.0, [1, 0, 2, 3]),
        (15.0, [1, 0, 0, 1]),
        (100.0, [1, 0, 0, 1]),
    ],
)
def test_simple3(mutate: bool, threshold: float, expected: list):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3],
            "ancestor_list": ["[None]", "[None]", "[0]", "[1]"],
            "origin_time": [20, 10, 30, 45],
        }
    )
    original_df = phylogeny_df.copy()
    result = alifestd_calc_clade_lookback_origin_time_delta_asexual(
        phylogeny_df,
        lookback_origin_time_delta=threshold,
        mutate=mutate,
    )
    assert isinstance(result, np.ndarray)
    assert result.tolist() == expected
    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize(
    "threshold, expected",
    [
        (0.0, [1, 0, 2, 3]),
        (24.0, [0, 0, 0, 1]),
        (25.0, [0, 0, 0, 1]),
        (100.0, [0, 0, 0, 0]),
    ],
)
def test_simple4(mutate: bool, threshold: float, expected: list):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3],
            "ancestor_list": ["[0]", "[None]", "[0]", "[1]"],
            "origin_time": [20, 10, 30, 45],
        }
    )
    original_df = phylogeny_df.copy()
    result = alifestd_calc_clade_lookback_origin_time_delta_asexual(
        phylogeny_df,
        lookback_origin_time_delta=threshold,
        mutate=mutate,
    )
    assert isinstance(result, np.ndarray)
    assert result.tolist() == expected
    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize(
    "threshold, expected",
    [
        (0.0, [0, 1, 2, 3]),
        (15.0, [0, 1, 0, 1]),
        (100.0, [0, 1, 0, 1]),
    ],
)
def test_simple5_sorted(mutate: bool, threshold: float, expected: list):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3],
            "ancestor_list": ["[None]", "[None]", "[0]", "[1]"],
            "origin_time": [20, 10, 30, 45],
        }
    ).sort_values("id")
    original_df = phylogeny_df.copy()
    result = alifestd_calc_clade_lookback_origin_time_delta_asexual(
        phylogeny_df,
        lookback_origin_time_delta=threshold,
        mutate=mutate,
    )
    assert isinstance(result, np.ndarray)
    assert result.tolist() == expected
    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize(
    "threshold, expected",
    [
        (0.0, [0, 1, 2, 3]),
        (25.0, [0, 0, 0, 1]),
        (100.0, [0, 0, 0, 0]),
    ],
)
def test_simple6_sorted(mutate: bool, threshold: float, expected: list):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3],
            "ancestor_list": ["[0]", "[None]", "[0]", "[1]"],
            "origin_time": [20, 10, 30, 45],
        }
    ).sort_values("id")
    original_df = phylogeny_df.copy()
    result = alifestd_calc_clade_lookback_origin_time_delta_asexual(
        phylogeny_df,
        lookback_origin_time_delta=threshold,
        mutate=mutate,
    )
    assert isinstance(result, np.ndarray)
    assert result.tolist() == expected
    if not mutate:
        assert original_df.equals(phylogeny_df)
