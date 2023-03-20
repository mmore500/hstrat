import typing


def deep_listify(maybe_iterable: typing.Iterable) -> typing.Any:
    """Recursively convert an iterable into a list, converting any nested
    iterables recusrively.

    Will not convert strings.

    Parameters
    ----------
    maybe_iterable
        The object to be converted.

    Returns
    -------
        A nested list containing the elements of `maybe_iterable` if `maybe_iterable` was iterable, else `maybe_iterable`.


    Examples
    --------
    >>> deep_listify(range(4))
    [0, 1, 2, 3]

    >>> deep_listify(4)
    4

    >>> deep_listify([(1, 2), 3, 4])
    [[1, 2], 3, 4]

    >>> deep_listify([1, [2, (3, 4)], 5])
    [1, [2, [3, 4]], 5]

    >>> deep_listify(iter([1, range(2), 3]))
    [1, [0, 1], 3]
    """
    try:
        if isinstance(maybe_iterable, str):
            raise TypeError
        else:
            return [*map(deep_listify, maybe_iterable)]
    except TypeError:
        return maybe_iterable
