import statistics
import typing

import opytional as opyt

from ...._auxiliary_lib import cmp_approx, pairwise, unzip
from ....genome_instrumentation import HereditaryStratigraphicColumn
from ....juxtaposition._impl import (
    iter_ranks_of_retained_commonality_between_generic,
)
from ._extract_common_retained_ranks_through_first_retained_disparity import (
    extract_common_retained_ranks_through_first_retained_disparity,
)


def estimate_rank_of_mrca_maximum_likelihood(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    prior_interval_weight: typing.Callable[[int, int], float],
    prior_interval_expected: typing.Callable[[int, int], float],
) -> typing.Optional[float]:

    waypoints_ascending = (
        extract_common_retained_ranks_through_first_retained_disparity(
            first, second
        )
    )
    if len(waypoints_ascending) == 1:
        return None

    base = 1 / 2 ** first.GetStratumDifferentiaBitWidth()
    max_weight, best_expected_rank = max(
        (
            # weight
            (
                base**num_spurious_collisions
                * prior_interval_weight(begin_inclusive, end_exclusive)
            ),
            # expected rank
            # assumes monotonicity of prior
            {
                1: end_exclusive - 1,
                0: statistics.mean((end_exclusive - 1, begin_inclusive)),
                -1: begin_inclusive,
            }[
                cmp_approx(
                    prior_interval_expected(begin_inclusive, end_exclusive),
                    statistics.mean((end_exclusive - 1, begin_inclusive)),
                )
            ],
        )
        for (
            num_spurious_collisions,
            (
                end_exclusive,
                begin_inclusive,
            ),
        ) in enumerate(pairwise(reversed(waypoints_ascending)))
    )

    return best_expected_rank
