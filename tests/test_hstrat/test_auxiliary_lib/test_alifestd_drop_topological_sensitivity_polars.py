import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_drop_topological_sensitivity_polars,
)
from hstrat._auxiliary_lib._alifestd_check_topological_sensitivity import (
    _topologically_sensitive_cols,
    _update_only_sensitive_cols,
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


def test_drop_none(base_df):
    result = alifestd_drop_topological_sensitivity_polars(base_df)
    assert set(result.columns) == set(base_df.columns)


@pytest.mark.parametrize("col", sorted(_topologically_sensitive_cols))
def test_drop_single(base_df, col):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_drop_topological_sensitivity_polars(df)
    assert col not in result.columns
    assert "id" in result.columns


def test_drop_multiple(base_df):
    df = base_df.with_columns(
        pl.lit(0.0).alias("branch_length"),
        pl.lit(0).alias("node_depth"),
        pl.lit(0).alias("sister_id"),
        pl.lit("x").alias("taxon_label"),
    )
    result = alifestd_drop_topological_sensitivity_polars(df)
    assert "branch_length" not in result.columns
    assert "node_depth" not in result.columns
    assert "sister_id" not in result.columns
    assert "taxon_label" in result.columns
    assert "id" in result.columns


def test_preserves_non_sensitive(base_df):
    df = base_df.with_columns(
        pl.lit("x").alias("taxon_label"),
        pl.lit(True).alias("extant"),
        pl.lit(0.0).alias("branch_length"),
    )
    result = alifestd_drop_topological_sensitivity_polars(df)
    expected_cols = {
        "id", "ancestor_id", "origin_time", "taxon_label", "extant",
    }
    assert set(result.columns) == expected_cols


def test_empty():
    df = pl.DataFrame(
        {
            "id": pl.Series([], dtype=pl.Int64),
            "branch_length": pl.Series([], dtype=pl.Float64),
        }
    )
    result = alifestd_drop_topological_sensitivity_polars(df)
    assert "branch_length" not in result.columns
    assert "id" in result.columns
    assert len(result) == 0


@pytest.mark.parametrize("col", sorted(_update_only_sensitive_cols))
def test_insert_only_preserves_update_only(base_df, col):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_drop_topological_sensitivity_polars(
        df, insert=True, delete=False, update=False,
    )
    assert col in result.columns


@pytest.mark.parametrize(
    "col",
    sorted(_topologically_sensitive_cols - _update_only_sensitive_cols),
)
def test_insert_only_drops_structure_sensitive(base_df, col):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_drop_topological_sensitivity_polars(
        df, insert=True, delete=False, update=False,
    )
    assert col not in result.columns


@pytest.mark.parametrize("col", sorted(_update_only_sensitive_cols))
def test_delete_only_preserves_update_only(base_df, col):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_drop_topological_sensitivity_polars(
        df, insert=False, delete=True, update=False,
    )
    assert col in result.columns


@pytest.mark.parametrize(
    "col",
    sorted(_topologically_sensitive_cols - _update_only_sensitive_cols),
)
def test_delete_only_drops_structure_sensitive(base_df, col):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_drop_topological_sensitivity_polars(
        df, insert=False, delete=True, update=False,
    )
    assert col not in result.columns


@pytest.mark.parametrize("col", sorted(_topologically_sensitive_cols))
def test_update_drops_all(base_df, col):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_drop_topological_sensitivity_polars(
        df, insert=False, delete=False, update=True,
    )
    assert col not in result.columns


def test_no_ops_drops_nothing(base_df):
    df = base_df.with_columns(
        pl.lit(0.0).alias("branch_length"),
        pl.lit(0).alias("sister_id"),
    )
    result = alifestd_drop_topological_sensitivity_polars(
        df, insert=False, delete=False, update=False,
    )
    assert "branch_length" in result.columns
    assert "sister_id" in result.columns
