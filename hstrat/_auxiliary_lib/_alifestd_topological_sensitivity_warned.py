import functools
import typing

import pandas as pd

from ._alifestd_drop_topological_sensitivity import (
    alifestd_drop_topological_sensitivity,
)
from ._alifestd_warn_topological_sensitivity import (
    alifestd_warn_topological_sensitivity,
)


def alifestd_topological_sensitivity_warned(
    *, insert: bool, delete: bool, update: bool
) -> typing.Callable:
    """Decorator that emits a topological sensitivity warning before the
    wrapped function executes.

    The first positional argument of the decorated function must be the
    phylogeny dataframe (pandas).

    The decorated function gains two additional keyword arguments:

    - ``ignore_topological_sensitivity`` (bool, default False):
      If True, suppress the topological sensitivity warning.
    - ``drop_topological_sensitivity`` (bool, default False):
      If True, drop topology-sensitive columns from the result and
      suppress the warning.

    Parameters
    ----------
    insert : bool
        Whether the operation inserts new nodes.
    delete : bool
        Whether the operation deletes nodes.
    update : bool
        Whether the operation updates ancestor relationships.

    Returns
    -------
    typing.Callable
        A decorator that wraps a function with topological sensitivity
        warning logic.

    See Also
    --------
    alifestd_topological_sensitivity_warned_polars :
        Polars-based implementation.
    alifestd_warn_topological_sensitivity :
        Underlying warning function.
    """

    def decorator(func: typing.Callable) -> typing.Callable:
        @functools.wraps(func)
        def wrapper(
            phylogeny_df: pd.DataFrame,
            *args: typing.Any,
            ignore_topological_sensitivity: bool = False,
            drop_topological_sensitivity: bool = False,
            **kwargs: typing.Any,
        ) -> pd.DataFrame:
            if (
                not ignore_topological_sensitivity
                and not drop_topological_sensitivity
            ):
                alifestd_warn_topological_sensitivity(
                    phylogeny_df,
                    func.__name__,
                    insert=insert,
                    delete=delete,
                    update=update,
                )
            result = func(phylogeny_df, *args, **kwargs)
            if drop_topological_sensitivity:
                result = alifestd_drop_topological_sensitivity(
                    result,
                    mutate=True,
                    insert=insert,
                    delete=delete,
                    update=update,
                )
            return result

        return wrapper

    return decorator
