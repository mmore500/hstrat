import numpy as np

from ._min_array_dtype import min_array_dtype


def as_compact_type(array: np.ndarray) -> np.ndarray:
    """
    Given an input numpy array, this function returns a copy of the input array
    cast to the most compact possible numpy datatype that can hold the values in the input array without overflow.

    Parameters
    ----------
    array : numpy.ndarray
        The input numpy array.

    Returns
    -------
    numpy.ndarray
        A copy of the input array cast to most compact possible numpy datatype
        that can hold the values in the input array without overflow.

    Notes
    -----
    Like `np.min_scalar_type` this method ignores loss of precision at values
    close to 0 (i.e., subnormal numbers).

    Examples
    --------
    >>> import numpy as np
    >>> from ._min_array_dtype import as_compact_type
    >>> arr = np.array([-1, 2, 3, 4, 5])
    >>> as_compact_type(arr)
    array([-1, 2, 3, 4, 5], dtype=int8)
    >>> arr = np.array([255, 256, 257])
    >>> as_compact_type(arr)
    array([255,   0,   1], dtype=uint8)
    """
    return array.astype(min_array_dtype(array))
