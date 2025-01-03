import typing

import numpy as np

from ._jit import jit


@jit(cache=False, nopython=True)
def iter_monotonic_equivalencies_reverse(
    first: np.ndarray,
    second: np.ndarray,
    start: typing.Tuple[int, int] = (-1, -1),
) -> typing.Iterator[typing.Tuple[int, int]]:
    """Find the indices of equivalent elements in two sorted arrays.

    Given two sorted arrays `first` and `second`, this function returns an
    iterator that yields pairs of indices (i, j) such that first[i] ==
    second[j]. The iteration stops when one of the arrays is fully traversed.

    Parameters
    ----------
    first : np.ndarray
        A sorted numpy array.
    second : np.ndarray
        A sorted numpy array.
    start : tuple of int, default (0, 0)
        A pair of indices (i, j) where the search should start. The
        search will begin at the element first[i] and second[j]. Default
        is (0, 0).

    Yields
    ------
    (i, j) : tuple of int
        A tuple of indices (i, j) where first[i] == second[j].

    See Also
    --------
    iter_monotonic_equivalencies

    Examples
    --------
    >>> first = np.array([1, 2, 3, 4, 5])
    >>> second = np.array([2, 4, 6, 8, 10])
    >>> for i, j in iter_monotonic_equivalencies(first, second, start=(1, 0)):
    ...     print(f"{i} {j}")
    1 0
    3 1

    """
    idx1, idx2 = start
    if idx1 < 0:
        idx1 += len(first)
    if idx2 < 0:
        idx2 += len(second)

    assert -1 <= idx1 < len(first)
    assert -1 <= idx2 < len(second)

    while idx1 >= 0 and idx2 >= 0:
        val1 = first[idx1]
        val2 = second[idx2]

        if val1 > val2:
            idx1 -= 1
        elif val1 < val2:
            idx2 -= 1
        else:  # val1 == val2
            yield (idx1, idx2)
            idx1 -= 1
            idx2 -= 1
