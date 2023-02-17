import random

import pytest

from hstrat._auxiliary_lib import assign_intersecting_subsets


@pytest.mark.parametrize(
    "ranges, expected_subsets_indices, expected_subsets_ranges",
    [
        (
            [(0, 1), (2, 3), (4, 5)],
            [[0], [1], [2]],
            [[(0, 1)], [(2, 3)], [(4, 5)]],
        ),
        (
            [(0, 2), (1, 2), (2, 3)],
            [[0, 1], [2]],
            [[(0, 2), (1, 2)], [(2, 3)]],
        ),
        (
            [(0, 5), (1, 2), (2, 3)],
            [[0, 1], [2]],
            [[(0, 5), (1, 2)], [(2, 3)]],
        ),
        (
            [(0, 5), (1, 2), (2, 3), (3, 3)],
            [[0, 1], [2], [3]],
            [[(0, 5), (1, 2)], [(2, 3)], [(3, 3)]],
        ),
        ([(0, 1)], [[0, 1]], [[(0, 1)]]),
        ([], [], []),
        (
            [(0, 2), (1, 2), (2, 3)],
            [[0, 1], [2]],
            [[(0, 2), (1, 2)], [(2, 3)]],
        ),
        (
            [(0, 2), (1, 2), (2, 2)],
            [[0, 1], [2]],
            [[(0, 2), (1, 2)], [(2, 2)]],
        ),
        (
            [(0, 1), (0, 1)],
            [[0, 1]],
            [[(0, 1), (0, 1)]],
        ),
        (
            [(0, 3), (1, 2), (1, 3)],
            [[0, 1, 2]],
            [[(0, 3), (1, 2), (1, 3)]],
        ),
        (
            [(1, 2), (2, 5), (2, 5), (0, 4), (3, 4)],
            [[0, 3], [1, 2, 4]],
            [[(0, 4), (1, 2)], [(2, 5), (2, 5), (3, 4)]],
        ),
    ],
)
def test_assign_intersecting_subsets(
    ranges, expected_subsets_indices, expected_subsets_ranges
):

    for _rep in range(20):
        created_subsets_indices = assign_intersecting_subsets(ranges)
        for (
            created_subset_indices,
            expected_subset_indices,
            expected_subset_ranges,
        ) in zip(
            created_subsets_indices,
            expected_subsets_indices,
            expected_subsets_ranges,
        ):
            assert sorted(created_subset_indices) == sorted(
                expected_subset_indices
            ) or len(ranges) > len(set(ranges))

            created_subset_ranges = [ranges[i] for i in created_subset_indices]
            assert sorted(created_subset_ranges) == sorted(
                expected_subset_ranges
            )

        random.shuffle(ranges)
