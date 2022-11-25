import operator
import typing

from ...genome_instrumentation import HereditaryStratigraphicColumn
from ._calc_rank_of_earliest_detectable_mrca_between import (
    calc_rank_of_earliest_detectable_mrca_between,
)
from ._calc_rank_of_mrca_bounds_between import calc_rank_of_mrca_bounds_between


def calc_rank_of_mrca_uncertainty_between(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    confidence_level: float = 0.95,
) -> typing.Optional[int]:
    """How wide is the estimate window for generation of MRCA?

    Calculate uncertainty of estimate for the number of depositions
    elapsed along the line of descent before the most common recent
    ancestor with second.

    Returns 0 if no common ancestor between first and second can be resolved
    with sufficient confidence. If insufficient common ranks between first
    and second are available to resolve any common ancestor, returns None.

    See Also
    --------
    calc_rank_of_mrca_bounds_between :
        Calculates bound whose uncertainty this method reports. See the
        corresponding docstring for explanation of parameters.
    """
    if (
        calc_rank_of_earliest_detectable_mrca_between(
            first,
            second,
            confidence_level=confidence_level,
        )
        is None
    ):
        return None

    bounds = calc_rank_of_mrca_bounds_between(
        first,
        second,
        confidence_level=confidence_level,
    )
    return 0 if bounds is None else abs(operator.sub(*bounds)) - 1
