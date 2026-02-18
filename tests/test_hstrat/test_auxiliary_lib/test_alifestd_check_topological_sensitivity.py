import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import alifestd_check_topological_sensitivity


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


class TestNonePresent:
    def test_pandas(self, base_df_pandas):
        result = alifestd_check_topological_sensitivity(base_df_pandas)
        assert result == []

    def test_polars(self, base_df_polars):
        result = alifestd_check_topological_sensitivity(base_df_polars)
        assert result == []


class TestSingleSensitiveCol:
    @pytest.mark.parametrize(
        "col",
        [
            "ancestor_origin_time",
            "branch_length",
            "edge_length",
            "origin_time_delta",
            "node_depth",
            "num_children",
            "num_descendants",
            "num_leaves",
            "sister_id",
            "left_child_id",
            "right_child_id",
            "is_left_child",
            "is_right_child",
            "max_descendant_origin_time",
            "clade_duration",
            "clade_subtended_duration",
            "clade_faithpd",
            "clade_duration_ratio_sister",
            "clade_subtended_duration_ratio_sister",
            "clade_leafcount_ratio_sister",
            "clade_nodecount_ratio_sister",
            "clade_fblr_growth_children",
            "clade_fblr_growth_sister",
            "clade_logistic_growth_children",
            "clade_logistic_growth_sister",
            "num_leaves_sibling",
            "num_preceding_leaves",
            "ot_mrca_id",
            "ot_mrca_time_of",
            "ot_mrca_time_since",
        ],
    )
    def test_pandas(self, base_df_pandas, col):
        df = base_df_pandas.copy()
        df[col] = 0
        result = alifestd_check_topological_sensitivity(df)
        assert result == [col]

    @pytest.mark.parametrize(
        "col",
        [
            "ancestor_origin_time",
            "branch_length",
            "edge_length",
            "origin_time_delta",
            "node_depth",
            "num_children",
        ],
    )
    def test_polars(self, base_df_polars, col):
        df = base_df_polars.with_columns(pl.lit(0).alias(col))
        result = alifestd_check_topological_sensitivity(df)
        assert result == [col]


class TestMultipleSensitiveCols:
    def test_pandas(self, base_df_pandas):
        df = base_df_pandas.copy()
        df["branch_length"] = 0
        df["node_depth"] = 0
        df["sister_id"] = 0
        result = alifestd_check_topological_sensitivity(df)
        assert result == ["branch_length", "node_depth", "sister_id"]

    def test_polars(self, base_df_polars):
        df = base_df_polars.with_columns(
            pl.lit(0).alias("branch_length"),
            pl.lit(0).alias("node_depth"),
            pl.lit(0).alias("sister_id"),
        )
        result = alifestd_check_topological_sensitivity(df)
        assert result == ["branch_length", "node_depth", "sister_id"]


class TestNonSensitiveColsIgnored:
    def test_pandas(self, base_df_pandas):
        df = base_df_pandas.copy()
        df["taxon_label"] = "x"
        df["extant"] = True
        result = alifestd_check_topological_sensitivity(df)
        assert result == []

    def test_polars(self, base_df_polars):
        df = base_df_polars.with_columns(
            pl.lit("x").alias("taxon_label"),
            pl.lit(True).alias("extant"),
        )
        result = alifestd_check_topological_sensitivity(df)
        assert result == []


class TestMixedSensitiveAndNonSensitive:
    def test_pandas(self, base_df_pandas):
        df = base_df_pandas.copy()
        df["taxon_label"] = "x"
        df["branch_length"] = 0.0
        df["extant"] = True
        df["ancestor_origin_time"] = 0
        result = alifestd_check_topological_sensitivity(df)
        assert result == ["ancestor_origin_time", "branch_length"]

    def test_polars(self, base_df_polars):
        df = base_df_polars.with_columns(
            pl.lit("x").alias("taxon_label"),
            pl.lit(0.0).alias("branch_length"),
            pl.lit(True).alias("extant"),
            pl.lit(0).alias("ancestor_origin_time"),
        )
        result = alifestd_check_topological_sensitivity(df)
        assert result == ["ancestor_origin_time", "branch_length"]


class TestNoMutation:
    def test_pandas(self, base_df_pandas):
        df = base_df_pandas.copy()
        df["branch_length"] = 0
        original = df.copy()
        alifestd_check_topological_sensitivity(df)
        pd.testing.assert_frame_equal(df, original)

    def test_polars(self, base_df_polars):
        df = base_df_polars.with_columns(
            pl.lit(0).alias("branch_length"),
        )
        original = df.clone()
        alifestd_check_topological_sensitivity(df)
        assert df.equals(original)


class TestEmptyDataFrame:
    def test_pandas(self):
        df = pd.DataFrame(
            {"id": pd.Series([], dtype=int), "ancestor_id": pd.Series([], dtype=int)}
        )
        assert alifestd_check_topological_sensitivity(df) == []

    def test_pandas_with_sensitive(self):
        df = pd.DataFrame(
            {
                "id": pd.Series([], dtype=int),
                "branch_length": pd.Series([], dtype=float),
            }
        )
        assert alifestd_check_topological_sensitivity(df) == [
            "branch_length"
        ]

    def test_polars(self):
        df = pl.DataFrame(
            {"id": pl.Series([], dtype=pl.Int64)}
        )
        assert alifestd_check_topological_sensitivity(df) == []

    def test_polars_with_sensitive(self):
        df = pl.DataFrame(
            {
                "id": pl.Series([], dtype=pl.Int64),
                "branch_length": pl.Series([], dtype=pl.Float64),
            }
        )
        assert alifestd_check_topological_sensitivity(df) == [
            "branch_length"
        ]


class TestReturnOrder:
    """Verify that returned columns follow the canonical order defined in
    _topologically_sensitive_cols, not the DataFrame column order."""

    def test_pandas(self, base_df_pandas):
        df = base_df_pandas.copy()
        # add in reverse alphabetical order
        df["sister_id"] = 0
        df["branch_length"] = 0
        df["ancestor_origin_time"] = 0
        result = alifestd_check_topological_sensitivity(df)
        assert result == [
            "ancestor_origin_time",
            "branch_length",
            "sister_id",
        ]

    def test_polars(self, base_df_polars):
        df = base_df_polars.with_columns(
            pl.lit(0).alias("sister_id"),
            pl.lit(0).alias("branch_length"),
            pl.lit(0).alias("ancestor_origin_time"),
        )
        result = alifestd_check_topological_sensitivity(df)
        assert result == [
            "ancestor_origin_time",
            "branch_length",
            "sister_id",
        ]
