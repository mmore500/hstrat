import typing

from ...._auxiliary_lib import HereditaryStratigraphicArtifact
from ....juxtaposition import calc_probability_differentia_collision_between
from ...estimators import (
    estimate_rank_of_mrca_unbiased as estimate_rank_of_mrca_unbiased_,
)
from ._extract_common_retained_ranks_through_first_retained_disparity import (
    extract_common_retained_ranks_through_first_retained_disparity,
)


def estimate_rank_of_mrca_unbiased(
    first: HereditaryStratigraphicArtifact,
    second: HereditaryStratigraphicArtifact,
    prior: typing.Any,
) -> typing.Optional[float]:
    """Forwards to estimate_rank_of_mrca_unbiased estimator."""
    waypoints_ascending = (
        extract_common_retained_ranks_through_first_retained_disparity(
            first, second
        )
    )
    return estimate_rank_of_mrca_unbiased_(
        reversed(waypoints_ascending),
        calc_probability_differentia_collision_between(first, second),
        prior,
    )
