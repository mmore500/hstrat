import functools
import itertools
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


def any_pandas_arg(arg: typing.Any, recurse: bool) -> bool:
    """Implementation detail for delegate_polars_implementation."""
    if isinstance(arg, (pd.DataFrame, pd.Series)):
        return True
    elif isinstance(arg, (pl.DataFrame, pl.Series, str)):
        return False

    if recurse:
        if isinstance(arg, _supported_mappings):
            return any(any_pandas_arg(v, recurse) for v in arg.values())
        elif isinstance(arg, _supported_iterables):
            return any(any_pandas_arg(ele, recurse) for ele in arg)
        elif isinstance(arg, (typing.Mapping, typing.Iterable)):
            warn_once(
                f"Container type '{type(arg).__name__}' cannot be checked for presence of Pandas"
            )

    return False


def any_polars_arg(arg: typing.Any, recurse: bool) -> bool:
    """
    Implementation detail for delegate_polars_implementation.
    Because coercion to Pandas will be done if there is no Polars function
    present, we must check for containers that contain Polars objects
    for which coercion is not implemented.
    """

    if isinstance(arg, (pl.DataFrame, pl.Series)):
        return True
    elif isinstance(arg, (pd.DataFrame, pd.Series, str)):
        return False

    if recurse:
        if isinstance(arg, _supported_mappings):
            return any(any_polars_arg(v, recurse) for v in arg.values())
        elif isinstance(arg, _supported_iterables):
            return any(any_polars_arg(ele, recurse) for ele in arg)
        elif isinstance(arg, (typing.Mapping, typing.Iterable)):
            warn_once(
                f"Container type '{type(arg).__name__}' cannot be checked for presence of Polars"
            )

    return False


def delegate_polars_implementation(
    polars_func: typing.Optional[typing.Callable] = None,
    recurse_type_checks: bool = False,
):
    """
    Returns a decorator for `original_func` using Pandas objects (i.e.
    DataFrame or Series) that detects if Polars objects are supplied
    instead. If they are, and `polars_func` not None, then `polars_func`
    is called instead. Otherwise, arguments are coerced to Pandas and
    `original_func` is called.

    If `recurse_type_checks` is True, then coercion and Polars/Pandas
    detection happens recursively, checking iterables and/or mappings.
    """

    def decorator(original_func: typing.Callable):
        @functools.wraps(original_func)
        def delegating_function(*args, **kwargs):

            any_pandas, any_polars = (
                any(
                    func(arg, recurse_type_checks)
                    for arg in itertools.chain(args, kwargs.values())
                )
                for func in (any_pandas_arg, any_polars_arg)
            )

            if any_pandas and any_polars:
                raise TypeError("mixing pandas and polars types is disallowed")
            elif any_polars and polars_func is not None:
                return polars_func(*args, **kwargs)
            else:
                args = (
                    *map(
                        lambda x: coerce_to_pandas(
                            x, recurse=recurse_type_checks
                        ),
                        args,
                    ),
                )
                kwargs = {
                    kw: coerce_to_pandas(arg, recurse=recurse_type_checks)
                    for kw, arg in kwargs.items()
                }
                pandas_retval = original_func(*args, **kwargs)
                if any_polars:
                    return coerce_to_polars(
                        pandas_retval, recurse=recurse_type_checks
                    )
                return pandas_retval

        if delegating_function.__doc__ is not None:
            delegating_function.__doc__ += (
                "\n\nThis function also accepts a polars.DataFrame, for which "
                f"there is {'not ' if polars_func is None else ''} a separate "
                "delegated function."
            )

        return delegating_function

    return decorator
