import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_drop_topological_sensitivity,
    alifestd_drop_topological_sensitivity_polars,
)


@pytest.fixture
def base_df_pandas():
    return pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 1],
            "origin_time": [0, 1, 2],
        }
    )


@pytest.fixture
def base_df_polars():
    return pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 1],
            "origin_time": [0, 1, 2],
        }
    )


class TestDropNone:
    def test_pandas(self, base_df_pandas):
        result = alifestd_drop_topological_sensitivity(base_df_pandas)
        pd.testing.assert_frame_equal(result, base_df_pandas)

    def test_polars(self, base_df_polars):
        result = alifestd_drop_topological_sensitivity_polars(base_df_polars)
        assert result.equals(base_df_polars)


class TestDropSingle:
    def test_pandas(self, base_df_pandas):
        df = base_df_pandas.copy()
        df["branch_length"] = [0.0, 1.0, 1.0]
        result = alifestd_drop_topological_sensitivity(df)
        assert "branch_length" not in result.columns
        assert "id" in result.columns
        assert "ancestor_id" in result.columns
        assert "origin_time" in result.columns

    def test_polars(self, base_df_polars):
        df = base_df_polars.with_columns(
            pl.lit(0.0).alias("branch_length"),
        )
        result = alifestd_drop_topological_sensitivity_polars(df)
        assert "branch_length" not in result.columns
        assert "id" in result.columns
        assert "ancestor_id" in result.columns
        assert "origin_time" in result.columns


class TestDropMultiple:
    def test_pandas(self, base_df_pandas):
        df = base_df_pandas.copy()
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

    def test_polars(self, base_df_polars):
        df = base_df_polars.with_columns(
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


class TestPreservesNonSensitive:
    def test_pandas(self, base_df_pandas):
        df = base_df_pandas.copy()
        df["taxon_label"] = "x"
        df["extant"] = True
        df["branch_length"] = 0.0
        result = alifestd_drop_topological_sensitivity(df)
        expected_cols = {"id", "ancestor_id", "origin_time", "taxon_label", "extant"}
        assert set(result.columns) == expected_cols

    def test_polars(self, base_df_polars):
        df = base_df_polars.with_columns(
            pl.lit("x").alias("taxon_label"),
            pl.lit(True).alias("extant"),
            pl.lit(0.0).alias("branch_length"),
        )
        result = alifestd_drop_topological_sensitivity_polars(df)
        expected_cols = {"id", "ancestor_id", "origin_time", "taxon_label", "extant"}
        assert set(result.columns) == expected_cols


class TestMutate:
    def test_pandas_mutate_false(self, base_df_pandas):
        df = base_df_pandas.copy()
        df["branch_length"] = 0.0
        original = df.copy()
        result = alifestd_drop_topological_sensitivity(df, mutate=False)
        pd.testing.assert_frame_equal(df, original)
        assert "branch_length" not in result.columns

    def test_pandas_mutate_true(self, base_df_pandas):
        df = base_df_pandas.copy()
        df["branch_length"] = 0.0
        result = alifestd_drop_topological_sensitivity(df, mutate=True)
        assert "branch_length" not in result.columns
        assert "branch_length" not in df.columns


class TestEmpty:
    def test_pandas(self):
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

    def test_polars(self):
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


class TestAllSensitiveColumns:
    """Test dropping all known sensitive columns at once."""

    def test_pandas(self, base_df_pandas):
        df = base_df_pandas.copy()
        sensitive = [
            "ancestor_origin_time",
            "branch_length",
            "clade_duration",
            "edge_length",
            "node_depth",
            "num_children",
            "num_descendants",
            "num_leaves",
            "origin_time_delta",
            "sister_id",
        ]
        for col in sensitive:
            df[col] = 0
        result = alifestd_drop_topological_sensitivity(df)
        for col in sensitive:
            assert col not in result.columns
        assert set(result.columns) == {"id", "ancestor_id", "origin_time"}

    def test_polars(self, base_df_polars):
        sensitive = [
            "ancestor_origin_time",
            "branch_length",
            "clade_duration",
            "edge_length",
            "node_depth",
            "num_children",
        ]
        df = base_df_polars.with_columns(
            *(pl.lit(0).alias(col) for col in sensitive)
        )
        result = alifestd_drop_topological_sensitivity_polars(df)
        for col in sensitive:
            assert col not in result.columns
        assert set(result.columns) == {"id", "ancestor_id", "origin_time"}
