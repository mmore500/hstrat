import warnings

from ._jit import jit

try:
    from numba import objmode
except (ImportError, ModuleNotFoundError):  # pragma: no cover
    import contextlib

    objmode = contextlib.nullcontext


def _warn(message: str) -> None:
    warnings.warn(message, RuntimeWarning)


@jit(nopython=True)
def jit_warn(message: str) -> None:
    """Issue a `RuntimeWarning` with `message`, including from within
    numba-jitted functions, by briefly entering numba object mode.

    Python's warning filters apply as usual; by default, each distinct
    message is shown once.
    """
    with objmode():
        _warn(message)
