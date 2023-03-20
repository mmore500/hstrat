import numbers
import typing

from ._intersect_ranges import intersect_ranges


def assign_intersecting_subsets(
    ranges: typing.List[typing.Tuple[numbers.Real, numbers.Real]],
) -> typing.List[typing.List[numbers.Integral]]:
    """Arrange ranges into groups such that all ranges within a group share at
    least one overlapping value.

    Composes groups such that intersected values are as low as possible. Put
    another way, ranges are preferentially associated with earlier groups.

    Returns groups with constituent ranges' indices in `ranges` instead of the
    ranges themselves.

    Parameters
    ----------
    ranges : list of tuples
        A list of tuples, each containing two real numbers representing the
        lwoer bound (inclusive) and upper bound (exclusive) of a range.

    Returns
    -------
    list of lists of tuples
        A list of lists, each containing integer values representing the
        indices of intersecting ranges within a group.


    Examples
    --------
    >>> make_intersecting_subsets([(1, 3), (5, 6), (2, 4)])
    [[0, 2], [1]]
    """

    range_subsets = []
    index_subsets = []
    for range_index, range_ in sorted(enumerate(ranges), key=lambda x: x[1]):
        for range_subset, index_subset in zip(range_subsets, index_subsets):
            if intersect_ranges([range_, *range_subset]):
                range_subset.append(range_)
                index_subset.append(range_index)
                break
        else:
            range_subsets.append([range_])
            index_subsets.append([range_index])

    return index_subsets
