import itertools as it
import typing
import warnings

from ..._auxiliary_lib import HereditaryStratigraphicArtifact
from ..pairwise import calc_rank_of_mrca_bounds_between
from ._calc_rank_of_earliest_detectable_mrca_among import (
    calc_rank_of_earliest_detectable_mrca_among,
)


def calc_rank_of_mrca_bounds_among(
    population: typing.Iterable[HereditaryStratigraphicArtifact],
    prior: str,
    confidence_level: float = 0.95,
) -> typing.Optional[typing.Tuple[int, int]]:
    """Within what generation range did MRCA fall?

    Calculate bounds on estimate for the number of depositions elapsed
    along the line of descent before the most recent common ancestor among population.

    Parameters
    ----------
    prior : {"arbitrary"}
        Prior probability density distribution over possible generations of the
        MRCA.

        Currently only "arbitrary" supported.
    confidence_level : float, optional
        Bounds must capture what probability of containing the true rank of
        the MRCA? Default 0.95.

    Returns
    -------
    (int, int), optional
        Inclusive lower and then exclusive upper bound on estimate or None
        if no common ancestor between first and second can be resolved with
        sufficient confidence. (Sufficient confidence depends on
        confidence_level.) Also returns None for empty or singleton population.

    Notes
    -----
    Currently implementaiton uses a naive O(n^2) approach. A more efficient
    implementation should be possible.

    The true rank of the MRCA is guaranteed to never fall above the bounds
    but may fall below.
    """
    assert 0.0 <= confidence_level <= 1.0

    pop_tee1, pop_tee2 = it.tee(population)
    if (
        calc_rank_of_earliest_detectable_mrca_among(
            pop_tee1,
            confidence_level=confidence_level,
        )
        is None
    ):
        warnings.warn(
            "Insufficient common ranks between columns to detect common "
            "ancestry at given confidence level."
        )
        return None

    pop_mrca_rank_lower_bound = float("inf")
    pop_mrca_rank_upper_bound = float("inf")
    any_combinations = False
    for (first, second) in it.combinations(pop_tee2, 2):
        any_combinations = True
        assert (
            first.GetStratumDifferentiaBitWidth()
            == second.GetStratumDifferentiaBitWidth()
        )
        mrca_rank_bounds = calc_rank_of_mrca_bounds_between(
            first,
            second,
            prior,
            confidence_level,
        )

        if mrca_rank_bounds is None:
            return None
        else:
            mrca_rank_lb, mrca_rank_ub = mrca_rank_bounds
            pop_mrca_rank_lower_bound = min(
                mrca_rank_lb, pop_mrca_rank_lower_bound
            )
            pop_mrca_rank_upper_bound = min(
                mrca_rank_ub, pop_mrca_rank_upper_bound
            )

    if not any_combinations:
        warnings.warn(
            "Empty or singleton population. Unable to calculate rank of MRCA "
            "bounds."
        )
        return None

    return (pop_mrca_rank_lower_bound, pop_mrca_rank_upper_bound)
