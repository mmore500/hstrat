import statistics
import typing

import opytional as opyt

from ...._auxiliary_lib import cmp_approx, pairwise, unzip
from ....genome_instrumentation import HereditaryStratigraphicColumn
from ....juxtaposition import calc_probability_differentia_collision_between
from ...estimators import (
    estimate_rank_of_mrca_maximum_likelihood as estimate_rank_of_mrca_maximum_likelihood_,
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
    p_collision = calc_probability_differentia_collision_between(first, second)
    base = 1 / 2 ** first.GetStratumDifferentiaBitWidth()

    return estimate_rank_of_mrca_maximum_likelihood_(
        reversed(waypoints_ascending),
        p_collision,
        prior,
    )
