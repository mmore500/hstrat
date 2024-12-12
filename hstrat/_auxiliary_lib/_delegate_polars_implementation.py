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


def _detect_pandas(arg: typing.Any, recurse: bool) -> bool:
    """Implementation detail for delegate_polars_implementation.

    If `recurse` is True, then this function will recursively check for Polars
    members in mappings and iterables.
    """
    if isinstance(arg, (pd.DataFrame, pd.Series)):
        return True
    elif isinstance(arg, (pl.DataFrame, pl.Series, str)):
        return False
    elif recurse and isinstance(arg, _supported_mappings):
        return any(_detect_pandas(v, recurse) for v in arg.values())
    elif recurse and isinstance(arg, _supported_iterables):
        return any(_detect_pandas(ele, recurse) for ele in arg)
    elif isinstance(arg, (typing.Mapping, typing.Iterable)):
        warn_once(
            f"Arguments of type '{type(arg).__name__}' "
            "cannot be checked for Polars members.",
        )
    else:
        return False


def _detect_polars(arg: typing.Any, recurse: bool) -> bool:
    """Implementation detail for delegate_polars_implementation.

    If `recurse` is True, then this function will recursively check for Polars
    members in mappings and iterables.
    """
    if isinstance(arg, (pl.DataFrame, pl.Series)):
        return True
    elif isinstance(arg, (pd.DataFrame, pd.Series, str)):
        return False
    elif recurse and isinstance(arg, _supported_mappings):
        return any(_detect_polars(v, recurse) for v in arg.values())
    elif recurse and isinstance(arg, _supported_iterables):
        return any(_detect_polars(ele, recurse) for ele in arg)
    elif recurse and isinstance(arg, (typing.Mapping, typing.Iterable)):
        warn_once(
            f"Arguments of type '{type(arg).__name__}' "
            "cannot be checked for Pandas members.",
        )
    else:
        return False


def delegate_polars_implementation(
    polars_impl: typing.Optional[typing.Callable] = None,
    recurse_type_checks: bool = False,
) -> typing.Callable:
    """Decorates `pandas_impl` to either (1) dynamically dispatches calls using
    polars arguments to a supplied polars implementation or (2) coerces
    arguments to Pandas and calls `pandas_impl`.

    Calls without Polars arguments are dispatched to `pandas_impl` without any
    coercion.

    If `recurse_type_checks` is True, then coercion and Polars/Pandas
    detection happens recursively, checking iterables and/or mappings.

    Raises
    ------
    TypeError
        If mixing Pandas and Polars arguments is detected.
    """
    recurse = recurse_type_checks
    coerce_to_pandas_ = functools.partial(coerce_to_pandas, recurse=recurse)
    coerce_to_polars_ = functools.partial(coerce_to_polars, recurse=recurse)
    detect_pandas_ = functools.partial(_detect_pandas, recurse=recurse)
    detect_polars_ = functools.partial(_detect_polars, recurse=recurse)

    def decorator(pandas_impl: typing.Callable) -> typing.Callable:
        @functools.wraps(pandas_impl)
        def delegating_function(*args, **kwargs) -> typing.Any:

            any_pandas = any(map(detect_pandas_, (*args, *kwargs.values())))
            any_polars = any(map(detect_polars_, (*args, *kwargs.values())))

            if any_pandas and any_polars:
                raise TypeError("mixing pandas and polars types is disallowed")
            elif any_polars and polars_impl is not None:
                return polars_impl(*args, **kwargs)
            else:
                args = [*map(coerce_to_pandas_, args)]
                kwargs = {
                    kw: coerce_to_pandas_(arg) for kw, arg in kwargs.items()
                }

                pandas_retval = pandas_impl(*args, **kwargs)

                if any_polars:
                    return coerce_to_polars_(pandas_retval)
                else:
                    return pandas_retval

        if delegating_function.__doc__ is not None:
            delegating_function.__doc__ += (
                "\n\nThis function also accepts a polars.DataFrame, for which "
                f"there is {'not ' if polars_impl is None else ''} a separate "
                "delegated implementation."
            )

        return delegating_function

    return decorator
