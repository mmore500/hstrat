import pandas as pd
import pytest

from hstrat._auxiliary_lib import alifestd_drop_chronological_sensitivity
from hstrat._auxiliary_lib._alifestd_check_chronological_sensitivity import (
    _chronologically_sensitive_cols,
    _reassign_only_sensitive_cols,
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


def test_drop_none(base_df: pd.DataFrame):
    original = base_df.copy()
    result = alifestd_drop_chronological_sensitivity(base_df)
    assert set(result.columns) == set(original.columns)


@pytest.mark.parametrize("col", sorted(_chronologically_sensitive_cols))
def test_drop_single(base_df: pd.DataFrame, col: str):
    df = base_df.copy()
    df[col] = 0
    result = alifestd_drop_chronological_sensitivity(df)
    assert col not in result.columns
    assert "id" in result.columns


def test_drop_multiple(base_df: pd.DataFrame):
    df = base_df.copy()
    df["branch_length"] = 0.0
    df["edge_length"] = 0
    df["ot_mrca_id"] = 0
    df["taxon_label"] = "x"
    result = alifestd_drop_chronological_sensitivity(df)
    assert "branch_length" not in result.columns
    assert "edge_length" not in result.columns
    assert "ot_mrca_id" not in result.columns
    assert "taxon_label" in result.columns
    assert "id" in result.columns


def test_preserves_non_sensitive(base_df: pd.DataFrame):
    df = base_df.copy()
    df["taxon_label"] = "x"
    df["extant"] = True
    df["branch_length"] = 0.0
    result = alifestd_drop_chronological_sensitivity(df)
    expected_cols = {
        "id",
        "ancestor_id",
        "origin_time",
        "taxon_label",
        "extant",
    }
    assert set(result.columns) == expected_cols


@pytest.mark.parametrize("mutate", [False, True])
def test_mutate(base_df: pd.DataFrame, mutate: bool):
    df = base_df.copy()
    df["branch_length"] = 0.0
    original = df.copy()
    result = alifestd_drop_chronological_sensitivity(df, mutate=mutate)
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
    result = alifestd_drop_chronological_sensitivity(df)
    assert "branch_length" not in result.columns
    assert "id" in result.columns
    assert len(result) == 0


@pytest.mark.parametrize("col", sorted(_reassign_only_sensitive_cols))
def test_shift_only_preserves_reassign_only(
    base_df: pd.DataFrame, col: str
):
    df = base_df.copy()
    df[col] = 0
    result = alifestd_drop_chronological_sensitivity(
        df,
        shift=True,
        rescale=False,
        reassign=False,
    )
    assert col in result.columns


@pytest.mark.parametrize(
    "col",
    sorted(_chronologically_sensitive_cols - _reassign_only_sensitive_cols),
)
def test_shift_only_drops_non_reassign_sensitive(
    base_df: pd.DataFrame, col: str
):
    df = base_df.copy()
    df[col] = 0
    result = alifestd_drop_chronological_sensitivity(
        df,
        shift=True,
        rescale=False,
        reassign=False,
    )
    assert col not in result.columns


@pytest.mark.parametrize("col", sorted(_reassign_only_sensitive_cols))
def test_rescale_only_preserves_reassign_only(
    base_df: pd.DataFrame, col: str
):
    df = base_df.copy()
    df[col] = 0
    result = alifestd_drop_chronological_sensitivity(
        df,
        shift=False,
        rescale=True,
        reassign=False,
    )
    assert col in result.columns


@pytest.mark.parametrize(
    "col",
    sorted(_chronologically_sensitive_cols - _reassign_only_sensitive_cols),
)
def test_rescale_only_drops_non_reassign_sensitive(
    base_df: pd.DataFrame, col: str
):
    df = base_df.copy()
    df[col] = 0
    result = alifestd_drop_chronological_sensitivity(
        df,
        shift=False,
        rescale=True,
        reassign=False,
    )
    assert col not in result.columns


@pytest.mark.parametrize("col", sorted(_chronologically_sensitive_cols))
def test_reassign_drops_all(base_df: pd.DataFrame, col: str):
    df = base_df.copy()
    df[col] = 0
    result = alifestd_drop_chronological_sensitivity(
        df,
        shift=False,
        rescale=False,
        reassign=True,
    )
    assert col not in result.columns


def test_no_ops_drops_nothing(base_df: pd.DataFrame):
    df = base_df.copy()
    df["branch_length"] = 0.0
    df["ot_mrca_id"] = 0
    result = alifestd_drop_chronological_sensitivity(
        df,
        shift=False,
        rescale=False,
        reassign=False,
    )
    assert "branch_length" in result.columns
    assert "ot_mrca_id" in result.columns
