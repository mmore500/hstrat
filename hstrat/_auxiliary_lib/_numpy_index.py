import typing

import numpy as np

from ._jit import jit


# adapted from https://stackoverflow.com/a/41578614
@jit(nopython=True)
def numpy_index(
    array: np.ndarray, item: typing.Any
) -> typing.Optional[typing.Tuple[int, ...]]:
    """Find the index of the first occurrence of a given item in a Numpy array.

    Parameters
    ----------
    array : numpy.ndarray
        The Numpy array to search.
    item : Any
        The item to search for in the array.

    Returns
    -------
    Tuple[int, ...] or None
        A tuple representing the index of the first occurrence of the given
        item in the array, or None if the item is not found in the array.

    Examples
    --------
    >>> a = np.array([1, 2, 3, 4, 5])
    >>> numpy_index(a, 3)
    (2,)
    >>> numpy_index(a, 6)
    None
    """
    for idx, val in np.ndenumerate(array):
        if val == item:
            return idx
    return None
