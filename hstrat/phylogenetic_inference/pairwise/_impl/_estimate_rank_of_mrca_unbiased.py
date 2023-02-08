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
    expected_ranks, weights = tuple(
        unzip(
            (
                # expected rank
                prior_interval_expected(begin_inclusive, end_exclusive),
                # weight
                (
                    base**num_spurious_collisions
                    * prior_interval_weight(begin_inclusive, end_exclusive)
                ),
            )
            for (
                num_spurious_collisions,
                (
                    end_exclusive,
                    begin_inclusive,
                ),
            ) in enumerate(pairwise(reversed(waypoints_ascending)))
        )
    )

    return np.average(
        np.array(expected_ranks),
        weights=np.array(weights),
    )
