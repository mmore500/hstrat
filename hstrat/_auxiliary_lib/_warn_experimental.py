import functools
import os
import typing
import warnings

from ._ExperimentalWarning import ExperimentalWarning


def _warn(name: str) -> None:
    if "HSTRAT_WARN_EXPERIMENTAL_SUPPRESS" not in os.environ:
        warnings.warn(
            f"{name} is experimental. Its interface and results can change "
            "in the future, and its results have not yet been "
            "validated, so they may be unreliable. To silence this "
            "warning, set the environment variable "
            "HSTRAT_WARN_EXPERIMENTAL_SUPPRESS, or filter hstrat's "
            "ExperimentalWarning category.",
            ExperimentalWarning,
            stacklevel=3,
        )


def warn_experimental(func: typing.Callable) -> typing.Callable:
    """Decorate a function or class as experimental, so that calling it (or,
    for a class, instantiating it) issues an `ExperimentalWarning`.

    Phrasing follows optuna's `experimental_func` decorator. Silence the
    warning by setting the environment variable
    `HSTRAT_WARN_EXPERIMENTAL_SUPPRESS`, or by filtering the
    `ExperimentalWarning` category.

    Parameters
    ----------
    func : Callable
        Function or class to decorate.

    Returns
    -------
    Callable
        Wrapped function, with `func`'s name and docstring, or, for a class,
        the class itself, with its `__init__` wrapped.
    """
    if isinstance(func, type):
        init = func.__init__

        @functools.wraps(init)
        def init_wrapper(*args, **kwargs) -> None:
            _warn(func.__name__)
            init(*args, **kwargs)

        func.__init__ = init_wrapper
        return func

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> typing.Any:
        _warn(func.__name__)
        return func(*args, **kwargs)

    return wrapper
