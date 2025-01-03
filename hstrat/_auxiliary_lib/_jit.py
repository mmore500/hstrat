import typing
import warnings

from ._is_in_coverage_run import is_in_coverage_run


class _ShimFtor:
    __wrapped__: typing.Callable  # shim for numba jit attr

    def __init__(self: "_ShimFtor", wrapped: typing.Callable) -> None:
        self.__wrapped__ = wrapped

    def __call__(self: "_ShimFtor", *args, **kwargs) -> typing.Any:
        return self.__wrapped__(*args, **kwargs)


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
        return _ShimFtor

    if is_in_coverage_run():
        warnings.warn(
            "code coverage tracing detected,"
            "disabling jit compilation to increase source visibility",
            RuntimeWarning,
        )
        return _ShimFtor
    else:  # pragma: no cover
        # exclude from coverage because jit compilation disabled in cov runs
        return nb.jit(*args, cache=kwargs.pop("cache", True), **kwargs)
