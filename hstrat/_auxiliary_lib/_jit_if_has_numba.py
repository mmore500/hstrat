import typing
import warnings


def jit_if_has_numba(*args, **kwargs) -> typing.Callable:
    """Decorator that performs jit compilation if numba available."""
    try:
        import numba as nb
    except ModuleNotFoundError as e:
        warnings.warn(
            "numba unavailable,"
            "wrapped function may lose significant performance",
            ImportWarning,
        )
        return lambda f: f
    else:
        return nb.jit(*args, **kwargs)
