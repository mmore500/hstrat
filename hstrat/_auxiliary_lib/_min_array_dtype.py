import numpy as np


def min_array_dtype(arr: np.ndarray) -> np.dtype:
    """Determine the most compact numpy dtype required to represent the values
    in the input array.

    Parameters
    ----------
    arr : numpy.ndarray
        Input array.

    Returns
    -------
    numpy.dtype
        The most compact dtype required to represent the values in the input
        array.

    Notes
    -----
    If the input array is empty, the function returns the result of
    `np.min_scalar_type(0)` as the default dtype.

    Like `np.min_scalar_type` this method ignores loss of precision at values
    close to 0 (i.e., subnormal numbers).

    Examples
    --------
    >>> arr = np.array([-129, 128])
    >>> dtype = min_array_dtype(arr)
    >>> print(dtype)
    int8
    """
    if len(arr) == 0:
        return np.min_scalar_type(0)

    min_, max_ = arr.min(), arr.max()
    if min_ >= 0:
        return np.min_scalar_type(max_)

    dtype_min = np.min_scalar_type(min_)
    conv = dtype_min.type(max_)
    if conv == max_ and np.isfinite(conv):
        return dtype_min
    else:
        assert abs(min_) < max_
        return np.min_scalar_type(-max_)
