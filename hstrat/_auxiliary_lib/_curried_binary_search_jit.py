import typing

import interval_search as inch

from ._jit import jit


def curried_binary_search_jit(predicate: typing.Callable[[int], bool]):
    """Find the positive integer threshold below which a search criteria is
    never satisfied and above which it is always satisfied.

    Currying allows for recursive calls that don't pass the predicate callable
    as an argument, which is necessary for compatibility with Numba jit
    compilation.

    Parameters
    ----------
    predicate : callable object
        Returns whether an integer value satisfies the search criteria.
    lower_bound : int
        Lower bound for the binary search, inclusive.
    upper_bound : int
        Upper bound for the binary search, inclusive.

    Returns
    -------
    searcher : Callable[[int, int], Optional[int]]
        The curried search function, which takes an optional integer
        `lower_bound` and `upper_bound` and returns the first integer value
        that satisfies the search criteria.

        If no value satisfies the search criteria, the curried search function will return None.
    """
    return inch.curried_binary_search(
        predicate, decorate_with=jit(nopython=True)
    )
