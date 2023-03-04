from collections import deque
import itertools as it
import typing


def flag_last(
    iterable: typing.Iterable,
) -> typing.Iterator[typing.Tuple[bool, typing.Any]]:
    """Yields tuples of the form (is_last, value) for each value in the
    iterable, where is_last is True if the value is the last in the iterable
    and False otherwise.

    Parameters
    ----------
    iterable : iterable
        The iterable to be processed.

    Yields
    ------
    flagged_value : tuple
        Tuples of the form (is_last, value) for each value in the iterable.

    Examples
    --------
    >>> [*flag_last([1, 2, 3, 4, 5])]
    [(False, 1), (False, 2), (False, 3), (False, 4), (True, 5)]

    >>> [*flag_last([1])]
    [(True, 1)]

    >>> [*flag_last([])]
    []

    """
    iterator = iter(iterable)
    lookahead = deque(it.islice(iterator, 2), maxlen=2)

    while lookahead:
        yield (len(lookahead) == 1, lookahead.popleft())
        for val in iterator:
            lookahead.append(val)
            break
