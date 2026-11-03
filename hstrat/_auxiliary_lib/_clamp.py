import typing

from ._jit import jit

_T = typing.TypeVar("_T")


@jit(nopython=True)
def clamp(value: _T, lo: _T, hi: _T) -> _T:
    """Clamp `value` to [`lo`, `hi`], with `std::clamp` semantics.

    Returns `lo` if `value < lo`, `hi` if `hi < value`, and `value`
    otherwise. Requires `not hi < lo`. Unlike `np.clip`, supports scalars
    within numba-jitted functions.
    """
    assert not hi < lo
    if value < lo:
        return lo
    elif hi < value:
        return hi
    else:
        return value
