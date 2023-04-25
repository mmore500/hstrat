import random

import pytest

from hstrat._auxiliary_lib import make_intersecting_subsets


@pytest.mark.parametrize(
    "ranges, expected_subsets",
    [
        (
            [(0, 1), (2, 3), (4, 5)],
            [[(0, 1)], [(2, 3)], [(4, 5)]],
        ),
        (
            [(0, 2), (1, 2), (2, 3)],
            [[(0, 2), (1, 2)], [(2, 3)]],
        ),
        (
            [(0, 5), (1, 2), (2, 3)],
            [[(0, 5), (1, 2)], [(2, 3)]],
        ),
        (
            [(0, 5), (1, 2), (2, 3), (3, 3)],
            [[(0, 5), (1, 2)], [(2, 3)], [(3, 3)]],
        ),
        ([(0, 1)], [[(0, 1)]]),
        ([], []),
        (
            [(0, 2), (1, 2), (2, 3)],
            [[(0, 2), (1, 2)], [(2, 3)]],
        ),
        (
            [(0, 2), (1, 2), (2, 2)],
            [[(0, 2), (1, 2)], [(2, 2)]],
        ),
        (
            [(0, 1), (0, 1)],
            [[(0, 1), (0, 1)]],
        ),
        (
            [(0, 3), (1, 2), (1, 3)],
            [[(0, 3), (1, 2), (1, 3)]],
        ),
        (
            [(1, 2), (2, 5), (2, 5), (0, 4), (3, 4)],
            [[(0, 4), (1, 2)], [(2, 5), (2, 5), (3, 4)]],
        ),
    ],
)
def test_make_intersecting_subsets(ranges, expected_subsets):

    for _rep in range(20):
        created_subsets = make_intersecting_subsets(ranges)
        for created_subset, expected_subset in zip(
            created_subsets, expected_subsets
        ):
            assert len(created_subset) == len(expected_subset)
            assert sorted(created_subset) == sorted(expected_subset)

        random.shuffle(ranges)
