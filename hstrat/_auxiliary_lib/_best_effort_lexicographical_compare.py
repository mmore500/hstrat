import typing


def best_effort_lexicographical_compare(
    first: typing.Iterable,
    second: typing.Iterable,
) -> bool:
    """
    Compare two iterables lexicographically, ignoring invalid
    comparisons.

    This function iterates over the elements of `first` and `second` in parallel
    and returns True if `first` comes before `second` in lexicographical order.
    If the two iterables are equal up to a certain point, but one iterable is
    shorter than the other, the shorter iterable is considered to come before
    the longer iterable.

    Parameters
    ----------
    first : iterable
        The first iterable to compare.
    second : iterable
        The second iterable to compare.

    Returns
    -------
    bool
        Does `first` come before `second` in lexicographical order?

    Example
    -------
    >>> best_effort_lexicographical_compare([1, 2, 3], [1, None, 2])
    True
    >>> best_effort_lexicographical_compare([1, 2, 3], [1, 2])
    False
    >>> best_effort_lexicographical_compare([1, 2], [1, 2, None])
    True
    """
    first_, second_ = iter(first), iter(second)
    for x, y in zip(first_, second_):
        try:
            if x == y:
                continue
            else:
                return x < y
        except TypeError:
            continue
    return any(True for __ in second_)
