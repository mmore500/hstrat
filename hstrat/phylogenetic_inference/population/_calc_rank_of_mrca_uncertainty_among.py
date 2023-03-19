import itertools as it
import operator
import typing

from ..._auxiliary_lib import HereditaryStratigraphicArtifact
from ._calc_rank_of_earliest_detectable_mrca_among import (
    calc_rank_of_earliest_detectable_mrca_among,
)
from ._calc_rank_of_mrca_bounds_among import calc_rank_of_mrca_bounds_among


def calc_rank_of_mrca_uncertainty_among(
    population: typing.Iterable[HereditaryStratigraphicArtifact],
    prior: str,
    confidence_level: float = 0.95,
) -> typing.Optional[int]:
    """How wide is the estimate window for generation of MRCA?

    Calculate uncertainty of estimate for the number of depositions
    elapsed along the line of descent before the most common recent
    ancestor with second.

    Returns 0 if no common ancestor between first and second can be resolved
    with sufficient confidence. If insufficient common ranks between first
    and second are available to resolve any common ancestor, returns None. If
    population is empty or singleton, also returns None.

    See Also
    --------
    calc_rank_of_mrca_bounds_among :
        Calculates bound whose uncertainty this method reports. See the
        corresponding docstring for explanation of parameters.
    """
    pop_tee1, pop_tee2 = it.tee(population)
    if (
        calc_rank_of_earliest_detectable_mrca_among(
            pop_tee1,
            confidence_level=confidence_level,
        )
        is None
    ):
        return None

    bounds = calc_rank_of_mrca_bounds_among(
        pop_tee2,
        prior=prior,
        confidence_level=confidence_level,
    )
    return 0 if bounds is None else abs(operator.sub(*bounds)) - 1
