import pandas as pd
import pytest

from hstrat._auxiliary_lib import alifestd_drop_topological_sensitivity
from hstrat._auxiliary_lib._alifestd_check_topological_sensitivity import (
    _topologically_sensitive_cols,
)


@pytest.fixture
def base_df():
    return pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 1],
            "origin_time": [0, 1, 2],
        }
    )


def test_drop_none(base_df):
    original = base_df.copy()
    result = alifestd_drop_topological_sensitivity(base_df)
    assert set(result.columns) == set(original.columns)


@pytest.mark.parametrize("col", sorted(_topologically_sensitive_cols))
def test_drop_single(base_df, col):
    df = base_df.copy()
    df[col] = 0
    result = alifestd_drop_topological_sensitivity(df)
    assert col not in result.columns
    assert "id" in result.columns


def test_drop_multiple(base_df):
    df = base_df.copy()
    df["branch_length"] = 0.0
    df["node_depth"] = 0
    df["sister_id"] = 0
    df["taxon_label"] = "x"
    result = alifestd_drop_topological_sensitivity(df)
    assert "branch_length" not in result.columns
    assert "node_depth" not in result.columns
    assert "sister_id" not in result.columns
    assert "taxon_label" in result.columns
    assert "id" in result.columns


def test_preserves_non_sensitive(base_df):
    df = base_df.copy()
    df["taxon_label"] = "x"
    df["extant"] = True
    df["branch_length"] = 0.0
    result = alifestd_drop_topological_sensitivity(df)
    expected_cols = {
        "id", "ancestor_id", "origin_time", "taxon_label", "extant",
    }
    assert set(result.columns) == expected_cols


@pytest.mark.parametrize("mutate", [False, True])
def test_mutate(base_df, mutate):
    df = base_df.copy()
    df["branch_length"] = 0.0
    original = df.copy()
    result = alifestd_drop_topological_sensitivity(df, mutate=mutate)
    assert "branch_length" not in result.columns
    if mutate:
        assert "branch_length" not in df.columns
    else:
        pd.testing.assert_frame_equal(df, original)


def test_empty():
    df = pd.DataFrame(
        {
            "id": pd.Series([], dtype=int),
            "branch_length": pd.Series([], dtype=float),
        }
    )
    result = alifestd_drop_topological_sensitivity(df)
    assert "branch_length" not in result.columns
    assert "id" in result.columns
    assert len(result) == 0
