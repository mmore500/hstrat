import numpy as np
import packaging


def numpy_fromiter_polyfill(iter_: iter, dtype) -> np.ndarray:
    """An implementation of `numpy.fromiter` that polyfills support for object
    dtype introduced in numpy version 1.23.

    If numpy is older than version 1.23, `iter_` will be unpacked into a list
    and the `np.array` constructor will be used. Otherwise, `numpy.fromiter`
    will be used.

    Optional arguments `count` and `like` are not supported.

    Parameters
    ----------
    iter_ : iterable
        An iterable object providing data for the array.
    dtype :
        The data-type of the returned array.

    Returns
    -------
    numpy.ndarray
        A numpy array containing the elements of the iterable.

    Examples
    --------
    >>> a = [1, 2, 3, 4, 5]
    >>> b = numpy_fromiter_polyfill(a, np.int32)
    >>> b
    array([1, 2, 3, 4, 5])
    """
    if (
        packaging.version.parse(np.__version__)
        < packaging.version.parse("1.23")
        and np.object_ == dtype
    ):
        return np.array([*iter_], dtype=dtype)
    else:
        return np.fromiter(
            iter_,
            dtype=dtype,
        )
