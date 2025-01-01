import polars as pl
import pytest

from hstrat._auxiliary_lib import get_sole_scalar_value_polars


def test_get_sole_scalar_value_polars_single_value():
    df = pl.DataFrame({"col": [42, 42, 42]})
    assert 42 == get_sole_scalar_value_polars(df, "col")
    assert 42 == get_sole_scalar_value_polars(df.lazy(), "col")


def test_get_sole_scalar_value_polars_multiple_values_error():
    df = pl.DataFrame({"col": [1, 2, 2]})
    with pytest.raises(ValueError):
        get_sole_scalar_value_polars(df, "col")
    with pytest.raises(ValueError):
        get_sole_scalar_value_polars(df.lazy(), "col")


def test_get_sole_scalar_value_polars_empty_dataframe_error():
    df = pl.DataFrame({"col": []})
    with pytest.raises(ValueError):
        get_sole_scalar_value_polars(df, "col")
    with pytest.raises(ValueError):
        get_sole_scalar_value_polars(df.lazy(), "col")
