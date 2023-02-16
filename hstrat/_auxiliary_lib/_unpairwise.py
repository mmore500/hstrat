import itertools as it
import typing


# adapted from https://stackoverflow.com/a/19564384
def unpairwise(
    iterable: typing.Iterable[typing.Tuple[typing.Any, typing.Any]]
) -> typing.Iterable:
    """Return an iterator that yields the first element of the first pair in
    iterable and then the second element of all pairs in iterable, effectively
    reversing a `pairwise` operation.

    Parameters
    ----------
    iterable : iterable
        A sequence of overlapping pairs to be "flattened".

    Returns
    -------
    iterator
        An iterator that interleaves the second element of each pair with the
        remaining elements in the input sequence.

    Notes
    -----
    This function is the precise inverse of pairwise, except in the singleton
    case when pairwise yields empty, effectively discarding the lone element.

    Examples
    --------
    >>> a = [(1, 2), (2, 3), (3, 4)]
    >>> list(unpairwise(a))
    [1, 2, 3, 4]
    """

    p = iter(iterable)
    return it.chain(next(p, []), (x[1] for x in p))
