import itertools as it
import typing
import warnings

from ..._auxiliary_lib import HereditaryStratigraphicArtifact
from ..pairwise import calc_rank_of_earliest_detectable_mrca_between


def calc_rank_of_earliest_detectable_mrca_among(
    population: typing.Iterable[HereditaryStratigraphicArtifact],
    confidence_level: float = 0.95,
) -> typing.Optional[int]:
    """After what generation is common ancstry robustly detectable?

    Calculates the earliest possible rank a MRCA among the population
    could be reliably detected at.

    Even if a true MRCA of the population exists, if it occured earlier
    than the rank calculated here it could not be reliably detected with
    sufficient confidence after accounting for the possibility of spurious
    differentia collisions. (Although subsequent spurious differentia
    collisions after the true MRCA of first and second could lead to MRCA
    detection at such a rank.)

    Returns None if insufficient common ranks exist with population
    to ever conclude at the given confidence level the existance of any
    common ancestry among th epopulation (even if all strata at common
    ranks had equivalent differentiae).

    Also returns None if population is empty or singleton.

    Notes
    -----
    Currently implementaiton uses a naive O(n^2) approach. A more efficient
    implementation should be possible.
    """

    earliest_detectable_mrca_rank = -1
    any_combinations = False
    for (first, second) in it.combinations(population, 2):
        any_combinations = True
        assert (
            first.GetStratumDifferentiaBitWidth()
            == second.GetStratumDifferentiaBitWidth()
        )
        earliest_detectable_mrca_rank_between = (
            calc_rank_of_earliest_detectable_mrca_between(
                first, second, confidence_level
            )
        )
        if earliest_detectable_mrca_rank_between is None:
            return None
        else:
            earliest_detectable_mrca_rank = max(
                earliest_detectable_mrca_rank,
                earliest_detectable_mrca_rank_between,
            )

    if not any_combinations:
        warnings.warn(
            "Empty or singleton population. Unable to calculate rank of "
            "earliest detectable MRCA."
        )
        return None

    return earliest_detectable_mrca_rank
