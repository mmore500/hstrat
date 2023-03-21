import typing


# adapted from https://stackoverflow.com/a/22115957
def unzip(
    iterable: typing.Iterable[typing.Tuple],
) -> typing.Iterator[typing.Tuple]:
    """Unzip the input iterable into an iterator of tuples where the nth output
    tuple contains the nth elements of each tuple in the input iterable.

    Parameters
    ----------
    iterable : typing.Iterable[typing.Tuple]
        An iterable of tuples to unzip.

    Returns
    -------
    typing.Iterator[typing.Tuple]
        An iterator of tuples where each tuple contains the nth elements from
        each of the tuples in the input iterable.

    Examples
    --------
    >>> list(unzip([(1, 2), (3, 4), (5, 6)]))
    [(1, 3, 5), (2, 4, 6)]
    Here, the first output tuple contains the first elements from each tuple in
    the input iterable, i.e. (1, 3, 5), while the second output tuple contains
    the second elements, i.e. (2, 4, 6).

    >>> list(unzip([(1, 2, 3), (4, 5, 6)]))
    [(1, 4), (2, 5), (3, 6)]
    Here, the first output tuple contains the first elements from each tuple in
    the input iterable, i.e. (1, 4), while the second output tuple contains the
    second elements, i.e. (2, 5), and the third output tuple contains the third
    elements, i.e. (3, 6).

    >>> list(unzip([(1,), (2,), (3,)]))
    [(1, 2, 3)]
    Here, the first output tuple contains the first and only element from each
    tuple in the input iterable, i.e. (1, 2, 3).
    """
    return zip(*iterable)
