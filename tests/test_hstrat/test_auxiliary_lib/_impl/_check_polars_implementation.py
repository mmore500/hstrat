import functools
import typing

import pandas as pd
import polars as pl

from hstrat._auxiliary_lib._delegate_polars_implementation import _coerce_to_pandas


def _coerce_to_polars(arg: typing.Any) -> typing.Any:
    if isinstance(arg, (pd.Series, pd.DataFrame)):
        return pl.from_pandas(arg)
    return arg


def check_polars_implementation(func: typing.Callable):
    @functools.wraps(func)
    def polars_equality_checker(*args, **kwargs):
        pl_args = tuple(_coerce_to_polars(arg) for arg in args)
        pl_kwargs = {kw: _coerce_to_polars(arg) for kw, arg in kwargs.items()}

        pd_result = func(*args, **kwargs)
        pl_result = func(*pl_args, **pl_kwargs)
        if isinstance(pl_result, pl.DataFrame):
            pl_result = _coerce_to_pandas(pl_result)
            pd.testing.assert_frame_equal(pl_result, pd_result)
        elif isinstance(pl_result, pl.Series):
            pl_result = _coerce_to_pandas(pl_result)
            pd.testing.assert_series_equal(
                pl_result, pd_result, check_names=False
            )
        else:
            assert pd_result == pl_result
        return pd_result

    return polars_equality_checker
