import functools
import typing

import pandas as pd
import polars as pl

DataFrame_T = typing.TypeVar("DataFrame_T", pd.DataFrame, pl.DataFrame)
Series_T = typing.TypeVar("Series_T", pd.Series, pl.Series)


def _coerce_to_pandas(obj: typing.Any) -> typing.Any:
    if hasattr(obj, "__dataframe__"):
        return pd.api.interchange.from_dataframe(obj, allow_copy=False)
    elif hasattr(obj, "to_pandas"):
        return obj.to_pandas()
    else:
        return obj


def delegate_polars_implementation(
    polars_func: typing.Optional[typing.Callable] = None,
):
    def decorator(original_func: typing.Callable):
        @functools.wraps(original_func)
        def delegating_function(*args, **kwargs):

            any_pandas = any(
                isinstance(arg, (pd.DataFrame, pd.Series))
                for arg in (*args, *kwargs.values())
            )
            any_polars = any(
                isinstance(arg, (pl.DataFrame, pl.Series))
                for arg in (*args, *kwargs.values())
            )
            if any_pandas and any_polars:
                raise TypeError("mixing pandas and polars types is disallowed")
            elif any_polars and polars_func is not None:
                return polars_func(*args, **kwargs)
            else:
                args = (*map(_coerce_to_pandas, args),)
                kwargs = {
                    kw: _coerce_to_pandas(arg) for kw, arg in kwargs.items()
                }
                return original_func(*args, **kwargs)

        if delegating_function.__doc__ is not None:
            delegating_function.__doc__ += (
                "\n\nThis function also accepts a polars.DataFrame, for which "
                f"there is {'not ' if polars_func is None else ''} a separate "
                "delegated function."
            )

        return delegating_function

    return decorator
