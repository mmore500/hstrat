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
    search_backwards: bool = False,
) -> typing.Optional[int]:
    """Find the index of the first occurrence of a given item in a Numpy array.

    Parameters
    ----------
    array : numpy.ndarray
        The Numpy array to search.
    item : Any
        The item to search for in the array.
    search_backwards : bool, default False
        If True, return the index of the last occurence of item. Otherwise, return first occurence.
    Returns
    -------
    int or None
        The index of the first (or last) occurrence of the given item in the
        array, or None if the item is not found in the array.

    Examples
    --------
    >>> a = np.array([1, 4, 3, 4, 5])
    >>> numpy_index_flat(a, 3)
    2,
    >>> numpy_index_flat(a, 6)
    None
    >>> numpy_index_flat(a, 3, search_backwards=True)
    3
    """
    # numba can't handle coexisting type possibilities for enumeration;
    # must spell out separately
    if search_backwards:
        enumeration = _reversed_enumerate_jit(array)
        for idx, val in enumeration:
            if val == item:
                return idx
        return None

    else:
        enumeration = enumerate(array)
        for idx, val in enumeration:
            if val == item:
                return idx
        return None
