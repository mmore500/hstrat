import functools
import typing
import warnings

import pandas as pd
import polars as pl

DataFrame_T = typing.TypeVar("DataFrame_T", pd.DataFrame, pl.DataFrame)
Series_T = typing.TypeVar("Series_T", pd.Series, pl.Series)


def delegate_polars_implementation(
    polars_func: typing.Optional[typing.Callable] = None,
):
    def decorator(original_func: typing.Callable):
        @functools.wraps(original_func)
        def delegating_function(*args, **kwargs):

            using_polars: typing.Optional[bool] = None

            def get_new_argument(
                arg: typing.Any,
            ) -> typing.Any:
                nonlocal using_polars
                if isinstance(arg, (pl.DataFrame, pl.Series)):
                    if using_polars is False:
                        raise ValueError(
                            "Using Polars and Pandas arguments in the same function is not allowed"
                        )
                    using_polars = True
                    if polars_func is None:
                        return arg.to_pandas()
                elif isinstance(arg, (pd.DataFrame, pd.Series)):
                    if using_polars is True:
                        raise ValueError(
                            "Using Polars and Pandas arguments in the same function is not allowed"
                        )
                    using_polars = False
                return arg

            args = tuple(get_new_argument(arg) for arg in args)
            kwargs = {kw: get_new_argument(arg) for kw, arg in kwargs.items()}

            if using_polars is True:
                if polars_func is None:
                    warnings.warn(
                        f"Function '{original_func.__name__}' does not have a delegated implementation for a polars DataFrame"
                    )
                    retval = original_func(*args, **kwargs)
                    return (
                        pl.from_pandas(retval)
                        if isinstance(retval, (pd.DataFrame, pd.Series))
                        else retval
                    )
                return polars_func(*args, **kwargs)
            return original_func(*args, **kwargs)

        if delegating_function.__doc__ is not None:
            delegating_function.__doc__ += (
                "\n\nThis function also accepts a polars.DataFrame, for which"
                f"there is {'not ' if polars_func is None else ''}a seperate delegated function"
            )
        for k, v in delegating_function.__annotations__.items():
            if v is pd.DataFrame:
                delegating_function.__annotations__[k] = DataFrame_T
            elif v is pd.Series:
                delegating_function.__annotations__[k] = Series_T

        return delegating_function

    return decorator
