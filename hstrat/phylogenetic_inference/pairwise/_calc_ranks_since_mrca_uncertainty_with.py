import operator
import typing

from ..._auxiliary_lib import HereditaryStratigraphicArtifact
from ._calc_rank_of_earliest_detectable_mrca_between import (
    calc_rank_of_earliest_detectable_mrca_between,
)
from ._calc_ranks_since_mrca_bounds_with import (
    calc_ranks_since_mrca_bounds_with,
)


def calc_ranks_since_mrca_uncertainty_with(
    focal: HereditaryStratigraphicArtifact,
    other: HereditaryStratigraphicArtifact,
    prior: typing.Literal["arbitrary"],
    confidence_level: float = 0.95,
) -> typing.Optional[int]:
    """How wide is the estimation window for generations elapsed since MRCA?

    Calculates uncertainty of estimate for the number of depositions
    elapsed along focal column's line of descent since the most common recent
    ancestor with other.

    Returns 0 if no common ancestor between focal and other can be resolved
    with sufficient confidence. If insufficient common ranks between focal
    and other are available to resolve any common ancestor, returns None.

    See Also
    --------
    calc_ranks_since_mrca_bounds_with :
        Calculates bound whose uncertainty this method reports. See the
        corresponding docstring for explanation of parameters.
    """
    assert 0.0 <= confidence_level <= 1.0

    if (
        calc_rank_of_earliest_detectable_mrca_between(
            focal,
            other,
            confidence_level=confidence_level,
        )
        is None
    ):
        return None

    bounds = calc_ranks_since_mrca_bounds_with(
        focal,
        other,
        prior=prior,
        confidence_level=confidence_level,
    )
    return 0 if bounds is None else abs(operator.sub(*bounds)) - 1
