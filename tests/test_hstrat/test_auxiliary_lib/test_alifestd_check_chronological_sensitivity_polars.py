import warnings

import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_check_chronological_sensitivity_polars,
    alifestd_warn_chronological_sensitivity_polars,
)
from hstrat._auxiliary_lib._alifestd_check_chronological_sensitivity import (
    _chronologically_sensitive_cols,
    _reassign_only_sensitive_cols,
)


@pytest.fixture
def base_df():
    return pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 1],
            "origin_time": [0, 1, 2],
        }
    )


def test_none_present(base_df: pl.DataFrame):
    result = alifestd_check_chronological_sensitivity_polars(
        base_df,
        shift=True,
        rescale=True,
        reassign=True,
    )
    assert result == []


@pytest.mark.parametrize("col", sorted(_chronologically_sensitive_cols))
def test_single_sensitive_col(base_df: pl.DataFrame, col: str):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_check_chronological_sensitivity_polars(
        df,
        shift=True,
        rescale=True,
        reassign=True,
    )
    assert result == [col]


def test_multiple_sensitive_cols(base_df: pl.DataFrame):
    df = base_df.with_columns(
        pl.lit(0).alias("branch_length"),
        pl.lit(0).alias("edge_length"),
        pl.lit(0).alias("ot_mrca_id"),
    )
    result = alifestd_check_chronological_sensitivity_polars(
        df,
        shift=True,
        rescale=True,
        reassign=True,
    )
    assert set(result) == {"branch_length", "edge_length", "ot_mrca_id"}


def test_non_sensitive_cols_ignored(base_df: pl.DataFrame):
    df = base_df.with_columns(
        pl.lit("x").alias("taxon_label"),
        pl.lit(True).alias("extant"),
    )
    result = alifestd_check_chronological_sensitivity_polars(
        df,
        shift=True,
        rescale=True,
        reassign=True,
    )
    assert result == []


def test_no_mutation(base_df: pl.DataFrame):
    df = base_df.with_columns(pl.lit(0).alias("branch_length"))
    original = df.clone()
    alifestd_check_chronological_sensitivity_polars(
        df,
        shift=True,
        rescale=True,
        reassign=True,
    )
    assert df.equals(original)


def test_empty_dataframe():
    df = pl.DataFrame({"id": pl.Series([], dtype=pl.Int64)})
    assert (
        alifestd_check_chronological_sensitivity_polars(
            df,
            shift=True,
            rescale=True,
            reassign=True,
        )
        == []
    )


def test_empty_dataframe_with_sensitive():
    df = pl.DataFrame(
        {
            "id": pl.Series([], dtype=pl.Int64),
            "branch_length": pl.Series([], dtype=pl.Float64),
        }
    )
    assert alifestd_check_chronological_sensitivity_polars(
        df,
        shift=True,
        rescale=True,
        reassign=True,
    ) == ["branch_length"]


@pytest.mark.parametrize("col", sorted(_chronologically_sensitive_cols))
def test_lazyframe(base_df: pl.DataFrame, col: str):
    df = base_df.with_columns(pl.lit(0).alias(col))
    lazy = df.lazy()
    result = alifestd_check_chronological_sensitivity_polars(
        lazy,
        shift=True,
        rescale=True,
        reassign=True,
    )
    assert result == [col]


def test_lazyframe_none_present(base_df: pl.DataFrame):
    lazy = base_df.lazy()
    result = alifestd_check_chronological_sensitivity_polars(
        lazy,
        shift=True,
        rescale=True,
        reassign=True,
    )
    assert result == []


@pytest.mark.parametrize("col", sorted(_reassign_only_sensitive_cols))
def test_shift_only_excludes_reassign_only(
    base_df: pl.DataFrame, col: str
):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_check_chronological_sensitivity_polars(
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
    base_df: pl.DataFrame, col: str
):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_check_chronological_sensitivity_polars(
        df,
        shift=True,
        rescale=False,
        reassign=False,
    )
    assert result == [col]


@pytest.mark.parametrize("col", sorted(_reassign_only_sensitive_cols))
def test_rescale_only_excludes_reassign_only(
    base_df: pl.DataFrame, col: str
):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_check_chronological_sensitivity_polars(
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
    base_df: pl.DataFrame, col: str
):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_check_chronological_sensitivity_polars(
        df,
        shift=False,
        rescale=True,
        reassign=False,
    )
    assert result == [col]


@pytest.mark.parametrize("col", sorted(_chronologically_sensitive_cols))
def test_reassign_includes_all(base_df: pl.DataFrame, col: str):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_check_chronological_sensitivity_polars(
        df,
        shift=False,
        rescale=False,
        reassign=True,
    )
    assert result == [col]


def test_no_ops_returns_empty(base_df: pl.DataFrame):
    cols = [
        pl.lit(0).alias(col) for col in _chronologically_sensitive_cols
    ]
    df = base_df.with_columns(cols)
    result = alifestd_check_chronological_sensitivity_polars(
        df,
        shift=False,
        rescale=False,
        reassign=False,
    )
    assert result == []


@pytest.mark.parametrize("col", sorted(_reassign_only_sensitive_cols))
def test_shift_only_lazyframe_excludes(base_df: pl.DataFrame, col: str):
    lazy = base_df.with_columns(pl.lit(0).alias(col)).lazy()
    result = alifestd_check_chronological_sensitivity_polars(
        lazy,
        shift=True,
        rescale=False,
        reassign=False,
    )
    assert col not in result


def test_warn_chronological_sensitivity_polars_warns(
    base_df: pl.DataFrame,
):
    df = base_df.with_columns(pl.lit(0).alias("branch_length"))
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        alifestd_warn_chronological_sensitivity_polars(
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


def test_warn_chronological_sensitivity_polars_silent(
    base_df: pl.DataFrame,
):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        alifestd_warn_chronological_sensitivity_polars(
            base_df,
            "test_caller",
            shift=True,
            rescale=True,
            reassign=True,
        )
        assert len(w) == 0


def test_warn_chronological_sensitivity_polars_lazyframe(
    base_df: pl.DataFrame,
):
    lazy = base_df.with_columns(
        pl.lit(0).alias("edge_length"),
    ).lazy()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        alifestd_warn_chronological_sensitivity_polars(
            lazy,
            "test_caller",
            shift=False,
            rescale=True,
            reassign=True,
        )
        assert len(w) == 1
        assert "edge_length" in str(w[0].message)


def test_warn_chronological_sensitivity_polars_ops_in_message(
    base_df: pl.DataFrame,
):
    df = base_df.with_columns(pl.lit(0).alias("branch_length"))
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        alifestd_warn_chronological_sensitivity_polars(
            df,
            "test_caller",
            shift=True,
            rescale=False,
            reassign=False,
        )
        assert len(w) == 1
        assert "shift" in str(w[0].message)
