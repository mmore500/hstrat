import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_drop_chronological_sensitivity_polars,
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


def test_drop_none(base_df: pl.DataFrame):
    result = alifestd_drop_chronological_sensitivity_polars(base_df)
    assert set(result.columns) == set(base_df.columns)


@pytest.mark.parametrize("col", sorted(_chronologically_sensitive_cols))
def test_drop_single(base_df: pl.DataFrame, col: str):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_drop_chronological_sensitivity_polars(df)
    assert col not in result.columns
    assert "id" in result.columns


def test_drop_multiple(base_df: pl.DataFrame):
    df = base_df.with_columns(
        pl.lit(0.0).alias("branch_length"),
        pl.lit(0).alias("edge_length"),
        pl.lit(0).alias("ot_mrca_id"),
        pl.lit("x").alias("taxon_label"),
    )
    result = alifestd_drop_chronological_sensitivity_polars(df)
    assert "branch_length" not in result.columns
    assert "edge_length" not in result.columns
    assert "ot_mrca_id" not in result.columns
    assert "taxon_label" in result.columns
    assert "id" in result.columns


def test_preserves_non_sensitive(base_df: pl.DataFrame):
    df = base_df.with_columns(
        pl.lit("x").alias("taxon_label"),
        pl.lit(True).alias("extant"),
        pl.lit(0.0).alias("branch_length"),
    )
    result = alifestd_drop_chronological_sensitivity_polars(df)
    expected_cols = {
        "id",
        "ancestor_id",
        "origin_time",
        "taxon_label",
        "extant",
    }
    assert set(result.columns) == expected_cols


def test_empty():
    df = pl.DataFrame(
        {
            "id": pl.Series([], dtype=pl.Int64),
            "branch_length": pl.Series([], dtype=pl.Float64),
        }
    )
    result = alifestd_drop_chronological_sensitivity_polars(df)
    assert "branch_length" not in result.columns
    assert "id" in result.columns
    assert len(result) == 0


@pytest.mark.parametrize("col", sorted(_reassign_only_sensitive_cols))
def test_shift_only_preserves_reassign_only(
    base_df: pl.DataFrame, col: str
):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_drop_chronological_sensitivity_polars(
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
    base_df: pl.DataFrame, col: str
):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_drop_chronological_sensitivity_polars(
        df,
        shift=True,
        rescale=False,
        reassign=False,
    )
    assert col not in result.columns


@pytest.mark.parametrize("col", sorted(_reassign_only_sensitive_cols))
def test_rescale_only_preserves_reassign_only(
    base_df: pl.DataFrame, col: str
):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_drop_chronological_sensitivity_polars(
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
    base_df: pl.DataFrame, col: str
):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_drop_chronological_sensitivity_polars(
        df,
        shift=False,
        rescale=True,
        reassign=False,
    )
    assert col not in result.columns


@pytest.mark.parametrize("col", sorted(_chronologically_sensitive_cols))
def test_reassign_drops_all(base_df: pl.DataFrame, col: str):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_drop_chronological_sensitivity_polars(
        df,
        shift=False,
        rescale=False,
        reassign=True,
    )
    assert col not in result.columns


def test_no_ops_drops_nothing(base_df: pl.DataFrame):
    df = base_df.with_columns(
        pl.lit(0.0).alias("branch_length"),
        pl.lit(0).alias("ot_mrca_id"),
    )
    result = alifestd_drop_chronological_sensitivity_polars(
        df,
        shift=False,
        rescale=False,
        reassign=False,
    )
    assert "branch_length" in result.columns
    assert "ot_mrca_id" in result.columns
