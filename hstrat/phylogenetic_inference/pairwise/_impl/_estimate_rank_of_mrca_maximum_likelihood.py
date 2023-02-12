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
    prior: typing.Any,
) -> typing.Optional[float]:

    waypoints_ascending = (
        extract_common_retained_ranks_through_first_retained_disparity(
            first, second
        )
    )
    if len(waypoints_ascending) == 1:
        return None

    base = 1 / 2 ** first.GetStratumDifferentiaBitWidth()

    max_weight, best_expected_rank = -1.0, None
    for (
        num_spurious_collisions,
        (
            end_exclusive,
            begin_inclusive,
        ),
    ) in enumerate(pairwise(reversed(waypoints_ascending))):
        cur_weight = (
            base**num_spurious_collisions
            * prior.CalcIntervalProbabilityProxy(
                begin_inclusive, end_exclusive
            )
        )

        if cur_weight > max_weight:
            max_weight = cur_weight
            # slide to most likely end of interval
            # assumes monotonicity of prior
            best_expected_rank = {
                1: end_exclusive - 1,
                0: statistics.mean((end_exclusive - 1, begin_inclusive)),
                -1: begin_inclusive,
            }[
                cmp_approx(
                    prior.CalcIntervalConditionedMean(
                        begin_inclusive, end_exclusive
                    ),
                    statistics.mean((end_exclusive - 1, begin_inclusive)),
                )
            ]

        # if whole rest of the remaining record cannot have higher cur_weight
        # than best, terminate early
        if (
            begin_inclusive
            and base ** (num_spurious_collisions + 1)
            * prior.CalcIntervalProbabilityProxy(
                0,
                begin_inclusive,
            )
            < max_weight
        ):
            break

    assert best_expected_rank is not None
    assert max_weight > 0.0

    return best_expected_rank
