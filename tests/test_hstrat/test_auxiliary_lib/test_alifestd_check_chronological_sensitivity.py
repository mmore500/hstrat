import warnings

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_check_chronological_sensitivity,
    alifestd_warn_chronological_sensitivity,
)
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


def test_none_present(base_df: pd.DataFrame):
    result = alifestd_check_chronological_sensitivity(
        base_df,
        shift=True,
        rescale=True,
        reassign=True,
    )
    assert result == []


@pytest.mark.parametrize("col", sorted(_chronologically_sensitive_cols))
def test_single_sensitive_col(base_df: pd.DataFrame, col: str):
    df = base_df.copy()
    df[col] = 0
    result = alifestd_check_chronological_sensitivity(
        df,
        shift=True,
        rescale=True,
        reassign=True,
    )
    assert result == [col]


def test_multiple_sensitive_cols(base_df: pd.DataFrame):
    df = base_df.copy()
    df["branch_length"] = 0
    df["edge_length"] = 0
    df["ot_mrca_id"] = 0
    result = alifestd_check_chronological_sensitivity(
        df,
        shift=True,
        rescale=True,
        reassign=True,
    )
    assert set(result) == {"branch_length", "edge_length", "ot_mrca_id"}


def test_non_sensitive_cols_ignored(base_df: pd.DataFrame):
    df = base_df.copy()
    df["taxon_label"] = "x"
    df["extant"] = True
    result = alifestd_check_chronological_sensitivity(
        df,
        shift=True,
        rescale=True,
        reassign=True,
    )
    assert result == []


def test_mixed_sensitive_and_non_sensitive(base_df: pd.DataFrame):
    df = base_df.copy()
    df["taxon_label"] = "x"
    df["branch_length"] = 0.0
    df["extant"] = True
    df["ancestor_origin_time"] = 0
    result = alifestd_check_chronological_sensitivity(
        df,
        shift=True,
        rescale=True,
        reassign=True,
    )
    assert set(result) == {"ancestor_origin_time", "branch_length"}


def test_no_mutation(base_df: pd.DataFrame):
    df = base_df.copy()
    df["branch_length"] = 0
    original = df.copy()
    alifestd_check_chronological_sensitivity(
        df,
        shift=True,
        rescale=True,
        reassign=True,
    )
    pd.testing.assert_frame_equal(df, original)


def test_empty_dataframe():
    df = pd.DataFrame(
        {
            "id": pd.Series([], dtype=int),
            "ancestor_id": pd.Series([], dtype=int),
        }
    )
    assert (
        alifestd_check_chronological_sensitivity(
            df,
            shift=True,
            rescale=True,
            reassign=True,
        )
        == []
    )


def test_empty_dataframe_with_sensitive():
    df = pd.DataFrame(
        {
            "id": pd.Series([], dtype=int),
            "branch_length": pd.Series([], dtype=float),
        }
    )
    assert alifestd_check_chronological_sensitivity(
        df,
        shift=True,
        rescale=True,
        reassign=True,
    ) == ["branch_length"]


@pytest.mark.parametrize("col", sorted(_reassign_only_sensitive_cols))
def test_shift_only_excludes_reassign_only(base_df: pd.DataFrame, col: str):
    df = base_df.copy()
    df[col] = 0
    result = alifestd_check_chronological_sensitivity(
        df,
        shift=True,
        rescale=False,
        reassign=False,
    )
    assert col not in result


@pytest.mark.parametrize(
    "col",
    sorted(_chronologically_sensitive_cols - _reassign_only_sensitive_cols),
)
def test_shift_only_includes_non_reassign_sensitive(
    base_df: pd.DataFrame, col: str
):
    df = base_df.copy()
    df[col] = 0
    result = alifestd_check_chronological_sensitivity(
        df,
        shift=True,
        rescale=False,
        reassign=False,
    )
    assert result == [col]


@pytest.mark.parametrize("col", sorted(_reassign_only_sensitive_cols))
def test_rescale_only_excludes_reassign_only(
    base_df: pd.DataFrame, col: str
):
    df = base_df.copy()
    df[col] = 0
    result = alifestd_check_chronological_sensitivity(
        df,
        shift=False,
        rescale=True,
        reassign=False,
    )
    assert col not in result


@pytest.mark.parametrize(
    "col",
    sorted(_chronologically_sensitive_cols - _reassign_only_sensitive_cols),
)
def test_rescale_only_includes_non_reassign_sensitive(
    base_df: pd.DataFrame, col: str
):
    df = base_df.copy()
    df[col] = 0
    result = alifestd_check_chronological_sensitivity(
        df,
        shift=False,
        rescale=True,
        reassign=False,
    )
    assert result == [col]


@pytest.mark.parametrize("col", sorted(_chronologically_sensitive_cols))
def test_reassign_includes_all(base_df: pd.DataFrame, col: str):
    df = base_df.copy()
    df[col] = 0
    result = alifestd_check_chronological_sensitivity(
        df,
        shift=False,
        rescale=False,
        reassign=True,
    )
    assert result == [col]


def test_no_ops_returns_empty(base_df: pd.DataFrame):
    df = base_df.copy()
    for col in sorted(_chronologically_sensitive_cols):
        df[col] = 0
    result = alifestd_check_chronological_sensitivity(
        df,
        shift=False,
        rescale=False,
        reassign=False,
    )
    assert result == []


def test_topological_only_cols_not_sensitive(base_df: pd.DataFrame):
    """Columns that are topologically sensitive but NOT chronologically
    sensitive should not be returned."""
    df = base_df.copy()
    df["node_depth"] = 0
    df["num_children"] = 0
    df["num_descendants"] = 0
    df["num_leaves"] = 0
    df["sister_id"] = 0
    df["is_left_child"] = False
    df["is_right_child"] = False
    result = alifestd_check_chronological_sensitivity(
        df,
        shift=True,
        rescale=True,
        reassign=True,
    )
    assert result == []


def test_warn_chronological_sensitivity_warns(base_df: pd.DataFrame):
    df = base_df.copy()
    df["branch_length"] = 0
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        alifestd_warn_chronological_sensitivity(
            df,
            "test_caller",
            shift=False,
            rescale=True,
            reassign=True,
        )
        assert len(w) == 1
        assert "test_caller" in str(w[0].message)
        assert "branch_length" in str(w[0].message)
        assert "rescale/reassign" in str(w[0].message)
        assert "alifestd_drop_chronological_sensitivity" in str(
            w[0].message,
        )


def test_warn_chronological_sensitivity_silent(base_df: pd.DataFrame):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        alifestd_warn_chronological_sensitivity(
            base_df,
            "test_caller",
            shift=True,
            rescale=True,
            reassign=True,
        )
        assert len(w) == 0


def test_warn_chronological_sensitivity_ops_in_message(
    base_df: pd.DataFrame,
):
    df = base_df.copy()
    df["ot_mrca_id"] = 0
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        alifestd_warn_chronological_sensitivity(
            df,
            "test_caller",
            shift=True,
            rescale=False,
            reassign=True,
        )
        assert len(w) == 1
        assert "shift/reassign" in str(w[0].message)
