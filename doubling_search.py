import typing

from . import binary_search


def doubling_search(
    predicate: typing.Callable[[int], bool],
    initial_guess: int=1,
) -> int:
    """
    Find the positive integer threshold below which a search criteria is never satisfied and above which it is always satisfied.

    Parameters
    ----------
    predicate : function
        Returns whether an integer value satisfies the search criteria.
    initial_guess : int, optional
        The initial guess.
        Should be less than or equal to the first value that satsfies the search criteria.
        Used for recursion.
        Default is 1.

    Returns
    -------
    guess
        The lowest integer value that satisfies the search criteria.
    """

    assert initial_guess >= 1, initial_guess

    bound = 1
    while not predicate(initial_guess + bound):
        bound *= 2

    prev_bound = bound // 2
    prev_guess = initial_guess + prev_bound
    return binary_search(predicate, prev_guess, initial_guess + bound)
