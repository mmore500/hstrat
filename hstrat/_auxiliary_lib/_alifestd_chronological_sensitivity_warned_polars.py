import functools
import typing

import polars as pl

from ._alifestd_drop_chronological_sensitivity_polars import (
    alifestd_drop_chronological_sensitivity_polars,
)
from ._alifestd_warn_chronological_sensitivity_polars import (
    alifestd_warn_chronological_sensitivity_polars,
)


def alifestd_chronological_sensitivity_warned_polars(
    *, shift: bool, rescale: bool, reassign: bool
) -> typing.Callable:
    """Decorator that emits a chronological sensitivity warning before the
    wrapped function executes.

    The first positional argument of the decorated function must be the
    phylogeny dataframe (polars).

    The decorated function gains two additional keyword arguments:

    - ``ignore_chronological_sensitivity`` (bool, default False):
      If True, suppress the chronological sensitivity warning.
    - ``drop_chronological_sensitivity`` (bool, default False):
      If True, drop chronology-sensitive columns from the result and
      suppress the warning.

    Parameters
    ----------
    shift : bool
        Whether the operation shifts origin times by a constant offset.
    rescale : bool
        Whether the operation rescales origin times by a constant factor.
    reassign : bool
        Whether the operation arbitrarily reassigns origin times.

    Returns
    -------
    typing.Callable
        A decorator that wraps a function with chronological sensitivity
        warning logic.

    See Also
    --------
    alifestd_chronological_sensitivity_warned :
        Pandas-based implementation.
    alifestd_warn_chronological_sensitivity_polars :
        Underlying warning function.
    """

    def decorator(func: typing.Callable) -> typing.Callable:
        @functools.wraps(func)
        def wrapper(
            phylogeny_df: typing.Union[pl.DataFrame, pl.LazyFrame],
            *args: typing.Any,
            ignore_chronological_sensitivity: bool = False,
            drop_chronological_sensitivity: bool = False,
            **kwargs: typing.Any,
        ) -> typing.Union[pl.DataFrame, pl.LazyFrame]:
            if (
                not ignore_chronological_sensitivity
                and not drop_chronological_sensitivity
            ):
                alifestd_warn_chronological_sensitivity_polars(
                    phylogeny_df,
                    func.__name__,
                    shift=shift,
                    rescale=rescale,
                    reassign=reassign,
                )
            result = func(phylogeny_df, *args, **kwargs)
            if drop_chronological_sensitivity:
                result = alifestd_drop_chronological_sensitivity_polars(
                    result,
                    shift=shift,
                    rescale=rescale,
                    reassign=reassign,
                )
            return result

        return wrapper

    return decorator
