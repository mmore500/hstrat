import functools
import typing

import pandas as pd
import polars as pl

from ._coerce_to_pandas import (
    _supported_iterables,
    _supported_mappings,
    coerce_to_pandas,
)
from ._coerce_to_polars import coerce_to_polars
from ._warn_once import warn_once

DataFrame_T = typing.TypeVar("DataFrame_T", pd.DataFrame, pl.DataFrame)
Series_T = typing.TypeVar("Series_T", pd.Series, pl.Series)


def any_pandas_arg(arg: typing.Any) -> bool:
    """Implementation detail for delegate_polars_implementation."""
    if isinstance(arg, str):  # edge case where iterating 'a' -> 'a' -> ...
        return False
    elif isinstance(arg, (pd.DataFrame, pd.Series)):
        return True
    elif isinstance(arg, _supported_mappings):
        return any(any_pandas_arg(v) for v in arg.values())
    elif isinstance(arg, _supported_iterables):
        return any(any_pandas_arg(ele) for ele in arg)
    elif isinstance(arg, (typing.Mapping, typing.Iterable)):
        warn_once(
            f"Container type '{type(arg)}' cannot be checked for presence of Pandas"
        )
    return False


def any_polars_arg(arg: typing.Any, polars_func_present: bool) -> bool:
    """
    Implementation detail for delegate_polars_implementation.
    Because coercion to Pandas will be done if there is no Polars function
    present, we must check for containers that contain Polars objects
    for which coercion is not implemented.
    """
    if isinstance(arg, str):  # edge case where iterating 'a' -> 'a' -> ...
        return False
    elif isinstance(arg, (pl.DataFrame, pl.Series)):
        return True
    elif isinstance(arg, _supported_mappings):
        return any(
            any_polars_arg(v, polars_func_present) for v in arg.values()
        )
    elif isinstance(arg, _supported_iterables):
        return any(any_polars_arg(ele, polars_func_present) for ele in arg)
    elif isinstance(arg, (typing.Mapping, typing.Iterable)):
        warn_once(
            f"Container type '{type(arg)}' cannot be checked for presence of Polars"
        )
    return False


def delegate_polars_implementation(
    polars_func: typing.Optional[typing.Callable] = None,
):
    """
    Returns a decorator for `original_func` using Pandas objects
    (i.e. DataFrame or Series) that detects if Polars objects are
    supplied instead. If they are, and `polars_func` is defined,
    then `polars_func` is called instead. Otherwise, arguments
    are coerced to Pandas and `original_func` is called.
    """

    def decorator(original_func: typing.Callable):
        @functools.wraps(original_func)
        def delegating_function(*args, **kwargs):

            any_pandas = any_pandas_arg(args + tuple(kwargs.values()))
            any_polars = any_polars_arg(
                args + tuple(kwargs.values()), polars_func is not None
            )
            if any_pandas and any_polars:
                raise TypeError("mixing pandas and polars types is disallowed")
            elif any_polars and polars_func is not None:
                return polars_func(*args, **kwargs)
            else:
                args = (*map(coerce_to_pandas, args),)
                kwargs = {
                    kw: coerce_to_pandas(arg) for kw, arg in kwargs.items()
                }
                pandas_retval = original_func(*args, **kwargs)
                if any_polars:
                    return coerce_to_polars(pandas_retval)
                return pandas_retval

        if delegating_function.__doc__ is not None:
            delegating_function.__doc__ += (
                "\n\nThis function also accepts a polars.DataFrame, for which "
                f"there is {'not ' if polars_func is None else ''} a separate "
                "delegated function."
            )

        return delegating_function

    return decorator
