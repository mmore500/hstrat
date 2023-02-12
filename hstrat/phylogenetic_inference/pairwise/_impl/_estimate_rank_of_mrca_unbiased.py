import statistics
import typing

import numpy as np
import opytional as opyt

from ...._auxiliary_lib import pairwise, unzip
from ....genome_instrumentation import HereditaryStratigraphicColumn
from ._extract_common_retained_ranks_through_first_retained_disparity import (
    extract_common_retained_ranks_through_first_retained_disparity,
)


# tried a numpy-based implementation but it was slower
# https://gist.github.com/mmore500/fc4caba18a98b20fbda3fb223cf49552
def estimate_rank_of_mrca_unbiased(
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

    weights, expected_ranks, sum_weight = [], [], 0.0
    for (
        num_spurious_collisions,
        (
            end_exclusive,
            begin_inclusive,
        ),
    ) in enumerate(pairwise(reversed(waypoints_ascending))):
        expected_ranks.append(
            prior.CalcIntervalConditionedMean(begin_inclusive, end_exclusive)
        )
        weights.append(
            base**num_spurious_collisions
            * prior.CalcIntervalProbabilityProxy(
                begin_inclusive, end_exclusive
            )
        )
        sum_weight += weights[-1]

        # if whole rest of the remaining record cannot meaningfully impact
        # average, exit early
        if (
            begin_inclusive
            and base ** (num_spurious_collisions + 1)
            * prior.CalcIntervalProbabilityProxy(
                0,
                begin_inclusive,
            ) * begin_inclusive
            < sum_weight * 10e-6  # numpy uses reltol 10e-5
        ):
            break

    return np.average(
        np.array(expected_ranks),
        weights=np.array(weights),
    )
