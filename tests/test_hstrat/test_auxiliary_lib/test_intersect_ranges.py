import pytest

from hstrat._auxiliary_lib import intersect_ranges


@pytest.mark.parametrize(
    "ranges, expected",
    [
        ([(0, 50), (3, 9), (7, 10)], (7, 9)),
        ([(1, 3), (3, 7), (3, 9)], None),
        ([(1, 5), (6, 8), (9, 12)], None),
        ([], None),
        ([(1, 2)], (1, 2)),
        ([(1, 1)], None),
        ([(1, 1), (2, 2), (3, 3)], None),
    ],
)
def test_intersect_ranges(ranges, expected):
    assert intersect_ranges(ranges) == expected
