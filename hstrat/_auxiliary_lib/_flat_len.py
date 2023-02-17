import typing


def flat_len(maybe_iterable: typing.Iterable) -> int:
    """Count the total number of elements in an iterable, recursing to count
    elements in any nested iterables.

    Examples
    --------
    >>> flat_len(range(4))
    4

    >>> flat_len(4)
    1

    >>> flat_len([(1, 2), 3, 4])
    4

    >>> flat_len([1, [2, (3, 4)], 5])
    [1, [2, [3, 4]], 5]

    >>> flat_len(iter([1, range(2), 3]))
    4
    """
    if isinstance(maybe_iterable, str):
        return len(maybe_iterable)
    try:
        return sum(map(flat_len, maybe_iterable))
    except TypeError:
        return 1
