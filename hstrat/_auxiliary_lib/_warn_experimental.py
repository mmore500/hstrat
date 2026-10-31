import functools
import os
import typing
import warnings

from ._ExperimentalWarning import ExperimentalWarning


def warn_experimental(func: typing.Callable) -> typing.Callable:
    """Decorate a function as experimental, so that calling it issues an
    `ExperimentalWarning`.

    Phrasing follows optuna's `experimental_func` decorator. Silence the
    warning by setting the environment variable
    `HSTRAT_WARN_EXPERIMENTAL_SUPPRESS`, or by filtering the
    `ExperimentalWarning` category.

    Parameters
    ----------
    func : Callable
        Function to decorate.

    Returns
    -------
    Callable
        Wrapped function, with `func`'s name and docstring.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> typing.Any:
        if "HSTRAT_WARN_EXPERIMENTAL_SUPPRESS" not in os.environ:
            warnings.warn(
                f"{func.__name__} is experimental. Its interface and results "
                "can change in the future. To silence this warning, set the "
                "environment variable HSTRAT_WARN_EXPERIMENTAL_SUPPRESS, "
                "or filter hstrat's ExperimentalWarning category.",
                ExperimentalWarning,
                stacklevel=2,
            )
        return func(*args, **kwargs)

    return wrapper
