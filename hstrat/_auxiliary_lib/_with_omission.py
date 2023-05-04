import itertools as it
import typing


def with_omission(
    iterable: typing.Iterable, omit_index: int
) -> typing.Generator:
    """Return an iterator that yields the elements of `iterable`, skipping over
    the element at index `omit_index`.

    Yields
    ------
    object
        The next element in the iterable with the specified index omitted.

    Examples
    --------
    >>> list(with_omission([1, 2, 3], 0))
    [2, 3]

    >>> list(with_omission('abcde', 2))
    ['a', 'b', 'd', 'e']

    >>> list(with_omission((1, 2, 3), 2))
    [1, 2]
    """

    iterator = iter(iterable)
    yield from it.islice(iterator, omit_index)
    next(iterator, None)
    yield from iterator
