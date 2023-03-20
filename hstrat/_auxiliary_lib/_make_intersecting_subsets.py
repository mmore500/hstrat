import numbers
import typing

from ._intersect_ranges import intersect_ranges


def make_intersecting_subsets(
    ranges: typing.List[typing.Tuple[numbers.Real, numbers.Real]],
) -> typing.List[typing.List[typing.Tuple[numbers.Real, numbers.Real]]]:
    """Arrange ranges into groups such that all ranges within a group share at
    least one overlapping value.

    Composes groups such that intersected values are as low as possible. Put
    another way, ranges are preferentially associated with earlier groups.

    Parameters
    ----------
    ranges : list of tuples
        A list of tuples, each containing two real numbers representing the
        lwoer bound (inclusive) and upper bound (exclusive) of a range.

    Returns
    -------
    list of lists of tuples
        A list of lists, each containing tuples representing the intersecting
        ranges within a group.


    Examples
    --------
    >>> make_intersecting_subsets([(1, 3), (2, 4), (5, 6)])
    [[(1, 3), (2, 4)], [(5, 6)]]
    """

    subsets = []
    for range_ in sorted(ranges):
        for subset in subsets:
            if intersect_ranges([range_, *subset]):
                subset.append(range_)
                break
        else:
            subsets.append([range_])

    return subsets
