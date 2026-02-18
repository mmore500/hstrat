import warnings

import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_check_topological_sensitivity_polars,
    alifestd_warn_topological_sensitivity_polars,
)
from hstrat._auxiliary_lib._alifestd_check_topological_sensitivity import (
    _insert_insensitive_cols,
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
    result = alifestd_check_topological_sensitivity_polars(
        base_df, insert=True, delete=True, update=True,
    )
    assert result == []


@pytest.mark.parametrize("col", sorted(_topologically_sensitive_cols))
def test_single_sensitive_col(base_df, col):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_check_topological_sensitivity_polars(
        df, insert=True, delete=True, update=True,
    )
    assert result == [col]


def test_multiple_sensitive_cols(base_df):
    df = base_df.with_columns(
        pl.lit(0).alias("branch_length"),
        pl.lit(0).alias("node_depth"),
        pl.lit(0).alias("sister_id"),
    )
    result = alifestd_check_topological_sensitivity_polars(
        df, insert=True, delete=True, update=True,
    )
    assert set(result) == {"branch_length", "node_depth", "sister_id"}


def test_non_sensitive_cols_ignored(base_df):
    df = base_df.with_columns(
        pl.lit("x").alias("taxon_label"),
        pl.lit(True).alias("extant"),
    )
    result = alifestd_check_topological_sensitivity_polars(
        df, insert=True, delete=True, update=True,
    )
    assert result == []


def test_no_mutation(base_df):
    df = base_df.with_columns(pl.lit(0).alias("branch_length"))
    original = df.clone()
    alifestd_check_topological_sensitivity_polars(
        df, insert=True, delete=True, update=True,
    )
    assert df.equals(original)


def test_empty_dataframe():
    df = pl.DataFrame({"id": pl.Series([], dtype=pl.Int64)})
    assert alifestd_check_topological_sensitivity_polars(
        df, insert=True, delete=True, update=True,
    ) == []


def test_empty_dataframe_with_sensitive():
    df = pl.DataFrame(
        {
            "id": pl.Series([], dtype=pl.Int64),
            "branch_length": pl.Series([], dtype=pl.Float64),
        }
    )
    assert alifestd_check_topological_sensitivity_polars(
        df, insert=True, delete=True, update=True,
    ) == ["branch_length"]


@pytest.mark.parametrize("col", sorted(_topologically_sensitive_cols))
def test_lazyframe(base_df, col):
    df = base_df.with_columns(pl.lit(0).alias(col))
    lazy = df.lazy()
    result = alifestd_check_topological_sensitivity_polars(
        lazy, insert=True, delete=True, update=True,
    )
    assert result == [col]


def test_lazyframe_none_present(base_df):
    lazy = base_df.lazy()
    result = alifestd_check_topological_sensitivity_polars(
        lazy, insert=True, delete=True, update=True,
    )
    assert result == []


@pytest.mark.parametrize("col", sorted(_insert_insensitive_cols))
def test_insert_only_excludes_insert_insensitive(base_df, col):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_check_topological_sensitivity_polars(
        df, insert=True, delete=False, update=False,
    )
    assert col not in result


@pytest.mark.parametrize(
    "col",
    sorted(_topologically_sensitive_cols - _insert_insensitive_cols),
)
def test_insert_only_includes_insert_sensitive(base_df, col):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_check_topological_sensitivity_polars(
        df, insert=True, delete=False, update=False,
    )
    assert result == [col]


@pytest.mark.parametrize("col", sorted(_topologically_sensitive_cols))
def test_delete_includes_all(base_df, col):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_check_topological_sensitivity_polars(
        df, insert=False, delete=True, update=False,
    )
    assert result == [col]


@pytest.mark.parametrize("col", sorted(_topologically_sensitive_cols))
def test_update_includes_all(base_df, col):
    df = base_df.with_columns(pl.lit(0).alias(col))
    result = alifestd_check_topological_sensitivity_polars(
        df, insert=False, delete=False, update=True,
    )
    assert result == [col]


def test_no_ops_returns_empty(base_df):
    cols = [pl.lit(0).alias(col) for col in _topologically_sensitive_cols]
    df = base_df.with_columns(cols)
    result = alifestd_check_topological_sensitivity_polars(
        df, insert=False, delete=False, update=False,
    )
    assert result == []


@pytest.mark.parametrize("col", sorted(_insert_insensitive_cols))
def test_insert_only_lazyframe_excludes(base_df, col):
    lazy = base_df.with_columns(pl.lit(0).alias(col)).lazy()
    result = alifestd_check_topological_sensitivity_polars(
        lazy, insert=True, delete=False, update=False,
    )
    assert col not in result


def test_warn_topological_sensitivity_polars_warns(base_df):
    df = base_df.with_columns(pl.lit(0).alias("branch_length"))
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        alifestd_warn_topological_sensitivity_polars(
            df, "test_caller",
            insert=False, delete=True, update=True,
        )
        assert len(w) == 1
        assert "test_caller" in str(w[0].message)
        assert "branch_length" in str(w[0].message)
        assert "delete/update" in str(w[0].message)
        assert "alifestd_drop_topological_sensitivity_polars" in str(
            w[0].message,
        )


def test_warn_topological_sensitivity_polars_silent(base_df):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        alifestd_warn_topological_sensitivity_polars(
            base_df, "test_caller",
            insert=True, delete=True, update=True,
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
            insert=False, delete=True, update=True,
        )
        assert len(w) == 1
        assert "edge_length" in str(w[0].message)


def test_warn_topological_sensitivity_polars_ops_in_message(base_df):
    df = base_df.with_columns(pl.lit(0).alias("sister_id"))
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        alifestd_warn_topological_sensitivity_polars(
            df, "test_caller",
            insert=True, delete=False, update=False,
        )
        assert len(w) == 1
        assert "insert" in str(w[0].message)
