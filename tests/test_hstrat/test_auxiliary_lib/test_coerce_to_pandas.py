import pandas as pd
import polars as pl

from hstrat._auxiliary_lib import coerce_to_pandas


def test_coerce_to_pandas_polars_lazyframe():
    lf = pl.LazyFrame({"a": [1, 2, 3]})
    result = coerce_to_pandas(lf)

    assert isinstance(result, pd.DataFrame)
    pd.testing.assert_frame_equal(result, pd.DataFrame({"a": [1, 2, 3]}))


def test_coerce_to_pandas_polars_dataframe():
    df = pl.DataFrame({"x": [10, 20], "y": [30, 40]})
    result = coerce_to_pandas(df)
    assert isinstance(result, pd.DataFrame)
    pd.testing.assert_frame_equal(
        result, pd.DataFrame({"x": [10, 20], "y": [30, 40]})
    )


def test_coerce_to_pandas_recurse_iterable():
    data = (pl.DataFrame({"a": [1, 2]}), 42, pl.DataFrame({"b": [3, 4]}))
    result = coerce_to_pandas(data, recurse=True)
    assert isinstance(result, tuple)
    assert len(result) == 3
    assert isinstance(result[0], pd.DataFrame)
    assert result[1] == 42
    assert isinstance(result[2], pd.DataFrame)


def test_coerce_to_pandas_no_coercion_needed():
    data = [1, 2, 3, "no-polars-here"]
    result = coerce_to_pandas(data)
    assert result == data
