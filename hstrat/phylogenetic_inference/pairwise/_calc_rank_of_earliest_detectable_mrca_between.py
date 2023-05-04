import typing

from ..._auxiliary_lib import HereditaryStratigraphicArtifact
from ...juxtaposition import (
    calc_min_implausible_spurious_consecutive_differentia_collisions_between,
    get_nth_common_rank_between,
)


def calc_rank_of_earliest_detectable_mrca_between(
    first: HereditaryStratigraphicArtifact,
    second: HereditaryStratigraphicArtifact,
    confidence_level: float = 0.95,
) -> typing.Optional[int]:
    """After what generation is common ancstry robustly detectable?

    Calculates the earliest possible rank a MRCA between first and second
    could be reliably detected at.

    Even if a true MRCA of first and second exists, if it occured earlier
    than the rank calculated here it could not be reliably detected with
    sufficient confidence after accounting for the possibility of spurious
    differentia collisions. (Although subsequent spurious differentia
    collisions after the true MRCA of first and second could lead to MRCA
    detection at such a rank.)

    Returns None if insufficient common ranks exist between first and second
    to ever conclude at the given confidence level the existance of any
    common ancestry between first and second (even if all strata at common
    ranks had equivalent differentiae).
    """
    assert (
        first.GetStratumDifferentiaBitWidth()
        == second.GetStratumDifferentiaBitWidth()
    )
    num_required_common_ranks = calc_min_implausible_spurious_consecutive_differentia_collisions_between(
        first,
        second,
        significance_level=1 - confidence_level,
    )
    # zero-indexed
    return get_nth_common_rank_between(
        first, second, num_required_common_ranks - 1
    )
