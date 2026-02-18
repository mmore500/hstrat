import warnings

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_check_topological_sensitivity,
    alifestd_warn_topological_sensitivity,
)
from hstrat._auxiliary_lib._alifestd_check_topological_sensitivity import (
    _topologically_sensitive_cols,
    _update_only_sensitive_cols,
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


def test_none_present(base_df: pd.DataFrame):
    result = alifestd_check_topological_sensitivity(
        base_df, insert=True, delete=True, update=True,
    )
    assert result == []


@pytest.mark.parametrize("col", sorted(_topologically_sensitive_cols))
def test_single_sensitive_col(base_df: pd.DataFrame, col: str):
    df = base_df.copy()
    df[col] = 0
    result = alifestd_check_topological_sensitivity(
        df, insert=True, delete=True, update=True,
    )
    assert result == [col]


def test_multiple_sensitive_cols(base_df: pd.DataFrame):
    df = base_df.copy()
    df["branch_length"] = 0
    df["node_depth"] = 0
    df["sister_id"] = 0
    result = alifestd_check_topological_sensitivity(
        df, insert=True, delete=True, update=True,
    )
    assert set(result) == {"branch_length", "node_depth", "sister_id"}


def test_non_sensitive_cols_ignored(base_df: pd.DataFrame):
    df = base_df.copy()
    df["taxon_label"] = "x"
    df["extant"] = True
    result = alifestd_check_topological_sensitivity(
        df, insert=True, delete=True, update=True,
    )
    assert result == []


def test_mixed_sensitive_and_non_sensitive(base_df: pd.DataFrame):
    df = base_df.copy()
    df["taxon_label"] = "x"
    df["branch_length"] = 0.0
    df["extant"] = True
    df["ancestor_origin_time"] = 0
    result = alifestd_check_topological_sensitivity(
        df, insert=True, delete=True, update=True,
    )
    assert set(result) == {"ancestor_origin_time", "branch_length"}


def test_no_mutation(base_df: pd.DataFrame):
    df = base_df.copy()
    df["branch_length"] = 0
    original = df.copy()
    alifestd_check_topological_sensitivity(
        df, insert=True, delete=True, update=True,
    )
    pd.testing.assert_frame_equal(df, original)


def test_empty_dataframe():
    df = pd.DataFrame(
        {
            "id": pd.Series([], dtype=int),
            "ancestor_id": pd.Series([], dtype=int),
        }
    )
    assert alifestd_check_topological_sensitivity(
        df, insert=True, delete=True, update=True,
    ) == []


def test_empty_dataframe_with_sensitive():
    df = pd.DataFrame(
        {
            "id": pd.Series([], dtype=int),
            "branch_length": pd.Series([], dtype=float),
        }
    )
    assert alifestd_check_topological_sensitivity(
        df, insert=True, delete=True, update=True,
    ) == ["branch_length"]


@pytest.mark.parametrize("col", sorted(_update_only_sensitive_cols))
def test_insert_only_excludes_update_only(base_df: pd.DataFrame, col: str):
    df = base_df.copy()
    df[col] = 0
    result = alifestd_check_topological_sensitivity(
        df, insert=True, delete=False, update=False,
    )
    assert col not in result


@pytest.mark.parametrize(
    "col",
    sorted(_topologically_sensitive_cols - _update_only_sensitive_cols),
)
def test_insert_only_includes_structure_sensitive(base_df: pd.DataFrame, col: str):
    df = base_df.copy()
    df[col] = 0
    result = alifestd_check_topological_sensitivity(
        df, insert=True, delete=False, update=False,
    )
    assert result == [col]


@pytest.mark.parametrize("col", sorted(_update_only_sensitive_cols))
def test_delete_only_excludes_update_only(base_df: pd.DataFrame, col: str):
    df = base_df.copy()
    df[col] = 0
    result = alifestd_check_topological_sensitivity(
        df, insert=False, delete=True, update=False,
    )
    assert col not in result


@pytest.mark.parametrize(
    "col",
    sorted(_topologically_sensitive_cols - _update_only_sensitive_cols),
)
def test_delete_only_includes_structure_sensitive(base_df: pd.DataFrame, col: str):
    df = base_df.copy()
    df[col] = 0
    result = alifestd_check_topological_sensitivity(
        df, insert=False, delete=True, update=False,
    )
    assert result == [col]


@pytest.mark.parametrize("col", sorted(_topologically_sensitive_cols))
def test_update_includes_all(base_df: pd.DataFrame, col: str):
    df = base_df.copy()
    df[col] = 0
    result = alifestd_check_topological_sensitivity(
        df, insert=False, delete=False, update=True,
    )
    assert result == [col]


def test_no_ops_returns_empty(base_df: pd.DataFrame):
    df = base_df.copy()
    for col in sorted(_topologically_sensitive_cols):
        df[col] = 0
    result = alifestd_check_topological_sensitivity(
        df, insert=False, delete=False, update=False,
    )
    assert result == []


def test_warn_topological_sensitivity_warns(base_df: pd.DataFrame):
    df = base_df.copy()
    df["branch_length"] = 0
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        alifestd_warn_topological_sensitivity(
            df, "test_caller",
            insert=False, delete=True, update=True,
        )
        assert len(w) == 1
        assert "test_caller" in str(w[0].message)
        assert "branch_length" in str(w[0].message)
        assert "delete/update" in str(w[0].message)
        assert "alifestd_drop_topological_sensitivity" in str(
            w[0].message,
        )


def test_warn_topological_sensitivity_silent(base_df: pd.DataFrame):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        alifestd_warn_topological_sensitivity(
            base_df, "test_caller",
            insert=True, delete=True, update=True,
        )
        assert len(w) == 0


def test_warn_topological_sensitivity_ops_in_message(base_df: pd.DataFrame):
    df = base_df.copy()
    df["sister_id"] = 0
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        alifestd_warn_topological_sensitivity(
            df, "test_caller",
            insert=True, delete=False, update=True,
        )
        assert len(w) == 1
        assert "insert/update" in str(w[0].message)
