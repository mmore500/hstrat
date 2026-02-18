import warnings

import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_check_topological_sensitivity_polars,
    alifestd_warn_topological_sensitivity_polars,
)
from hstrat._auxiliary_lib._alifestd_check_topological_sensitivity import (
    _topologically_sensitive_cols,
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


def test_none_present(base_df):
    result = alifestd_check_topological_sensitivity_polars(base_df)
    assert result == []


@pytest.mark.parametrize("col", sorted(_topologically_sensitive_cols))
def test_single_sensitive_col(base_df, col):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_check_topological_sensitivity_polars(df)
    assert result == [col]


def test_multiple_sensitive_cols(base_df):
    df = base_df.with_columns(
        pl.lit(0).alias("branch_length"),
        pl.lit(0).alias("node_depth"),
        pl.lit(0).alias("sister_id"),
    )
    result = alifestd_check_topological_sensitivity_polars(df)
    assert set(result) == {"branch_length", "node_depth", "sister_id"}


def test_non_sensitive_cols_ignored(base_df):
    df = base_df.with_columns(
        pl.lit("x").alias("taxon_label"),
        pl.lit(True).alias("extant"),
    )
    result = alifestd_check_topological_sensitivity_polars(df)
    assert result == []


def test_no_mutation(base_df):
    df = base_df.with_columns(pl.lit(0).alias("branch_length"))
    original = df.clone()
    alifestd_check_topological_sensitivity_polars(df)
    assert df.equals(original)


def test_empty_dataframe():
    df = pl.DataFrame({"id": pl.Series([], dtype=pl.Int64)})
    assert alifestd_check_topological_sensitivity_polars(df) == []


def test_empty_dataframe_with_sensitive():
    df = pl.DataFrame(
        {
            "id": pl.Series([], dtype=pl.Int64),
            "branch_length": pl.Series([], dtype=pl.Float64),
        }
    )
    assert alifestd_check_topological_sensitivity_polars(df) == [
        "branch_length"
    ]


@pytest.mark.parametrize("col", sorted(_topologically_sensitive_cols))
def test_lazyframe(base_df, col):
    df = base_df.with_columns(pl.lit(0).alias(col))
    lazy = df.lazy()
    result = alifestd_check_topological_sensitivity_polars(lazy)
    assert result == [col]


def test_lazyframe_none_present(base_df):
    lazy = base_df.lazy()
    result = alifestd_check_topological_sensitivity_polars(lazy)
    assert result == []


def test_warn_topological_sensitivity_polars_warns(base_df):
    df = base_df.with_columns(pl.lit(0).alias("branch_length"))
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        alifestd_warn_topological_sensitivity_polars(
            df, "test_caller",
        )
        assert len(w) == 1
        assert "test_caller" in str(w[0].message)
        assert "branch_length" in str(w[0].message)
        assert "alifestd_drop_topological_sensitivity_polars" in str(
            w[0].message,
        )


def test_warn_topological_sensitivity_polars_silent(base_df):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        alifestd_warn_topological_sensitivity_polars(
            base_df, "test_caller",
        )
        assert len(w) == 0


def test_warn_topological_sensitivity_polars_lazyframe(base_df):
    lazy = base_df.with_columns(
        pl.lit(0).alias("edge_length"),
    ).lazy()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        alifestd_warn_topological_sensitivity_polars(
            lazy, "test_caller",
        )
        assert len(w) == 1
        assert "edge_length" in str(w[0].message)
