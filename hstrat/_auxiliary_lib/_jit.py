import typing
import warnings

from ._is_in_coverage_run import is_in_coverage_run


def jit(*args, **kwargs) -> typing.Callable:
    """Decorator that performs jit compilation if numba available.

    Disables jit during coverage measurement to increase source
    visibility.
    """
    try:
        import numba as nb
    except (ImportError, ModuleNotFoundError):  # pragma: no cover
        warnings.warn(
            "numba unavailable,"
            "wrapped function may lose significant performance. "
            "To get numba, install it directly or install hstrat optional jit "
            "extras: python -m pip install hstrat[jit].",
            ImportWarning,
        )
        return lambda f: f

    if is_in_coverage_run():
        warnings.warn(
            "code coverage tracing detected,"
            "disabling jit compilation to increase source visibility",
            RuntimeWarning,
        )
        return lambda f: f
    else:  # pragma: no cover
        return nb.jit(*args, **kwargs)
