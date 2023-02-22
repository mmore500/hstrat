import typing

import numpy as np

from ._jit import jit
from ._reversed_enumerate import reversed_enumerate

_reversed_enumerate_jit = jit(nopython=True)(reversed_enumerate)

# adapted from https://stackoverflow.com/a/41578614
@jit(nopython=True)
def numpy_index_flat(
    array: np.ndarray,
    item: typing.Any,
    n: int = 0,
) -> typing.Optional[int]:
    """Find the index of the nth (zero-indexed) occurrence of a given item in a
    Numpy array.

    Parameters
    ----------
    array : numpy.ndarray
        The Numpy array to search.
    item : Any
        The item to search for in the array.
    n : int, default 0
        Specifies the zero-indexed nth occurrence of `item` to be
        found.

        If not specified or set to 0, the function returns the index of
        the first occurrence of `item`. If there are fewer than `n` occurrences
        of `item` in the array, the function returns None.

        If `n` is negative,
        the function returns the index of the nth occurrence from the end of
        the array (i.e., -1 returns the last occurrence, -2 returns the
        second-to-last occurrence, and so on).

    Returns
    -------
    int or None
        The index of the nth (zero-indexed) occurrence of the given item in the
        array, or None if the item is not found in the array.

    Examples
    --------
    >>> a = np.array([1, 4, 3, 4, 5])
    >>> numpy_index_flat(a, 3)
    2,
    >>> numpy_index_flat(a, 6)
    None
    >>> numpy_index_flat(a, 3, n=-1)
    3
    """
    # numba can't handle coexisting type possibilities for enumeration;
    # must spell out separately
    if n < 0:
        enumeration = _reversed_enumerate_jit(array)
        for idx, val in enumeration:
            if val == item:
                n += 1
            if n == 0:
                return idx
        return None

    else:
        enumeration = enumerate(array)
        for idx, val in enumeration:
            if val == item:
                n -= 1
            if n == -1:
                return idx
        return None
