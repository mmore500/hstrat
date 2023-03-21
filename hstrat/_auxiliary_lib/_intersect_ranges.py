import numbers
import typing

from ._unzip import unzip


def intersect_ranges(
    ranges: typing.Iterable[typing.Tuple[numbers.Real, numbers.Real]]
) -> typing.Optional[typing.Tuple[numbers.Real, numbers.Real]]:
    """Calculate the intersection of a collection of ranges.

    Parameters
    ----------
    ranges : iterable of tuples of real numbers
        A list of ranges represented as tuples of two real numbers,
        where the first number is the beginning of the range and the
        second number is the end of the range.

    Returns
    -------
    tuple of real numbers or None
        A tuple representing the intersection of the input ranges,
        where the first number is the beginning of the intersection and
        the second number is the end of the intersection. If there is no
        intersection, returns None.

    Examples
    --------
    >>> intersect_ranges([(0, 5), (3, 9), (3, 10)])
    (3, 5)

    >>> intersect_ranges([(1, 5)])
    (1, 5)

    >>> intersect_ranges([])
    None

    >>> intersect_ranges([(1, 3), (4, 7), (8, 10)])
    None
    """

    try:
        begins, ends = unzip(ranges)
    except ValueError:
        return None

    begin = max(begins)
    end = min(ends)

    return (begin, end) if begin < end else None
