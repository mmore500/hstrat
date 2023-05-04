import typing

from .._auxiliary_lib import HereditaryStratigraphicArtifact
from ._calc_min_implausible_spurious_consecutive_differentia_collisions_between import (
    calc_min_implausible_spurious_consecutive_differentia_collisions_between,
)
from ._calc_rank_of_first_retained_disparity_between import (
    calc_rank_of_first_retained_disparity_between,
)


def calc_definitive_max_rank_of_first_retained_disparity_between(
    first: HereditaryStratigraphicArtifact,
    second: HereditaryStratigraphicArtifact,
) -> typing.Optional[int]:
    """Determine hard, exclusive upper bound on MRCA generation.

    At most, how many depositions elapsed along the columns' lines of
    descent before the first mismatching strata at the same rank between
    self and second?

    Returns
    -------
    int, optional
        The number of depositions elapsed or None if no disparity (i.e.,
        both columns have same number of strata deposited and the most
        recent stratum is common between first and second).

    Notes
    -----
    If no mismatching strata are found but first and second have different
    numbers of strata deposited, this method returns one greater than the
    lesser of the columns' deposition counts.
    """
    confidence_level = 0.49
    assert (
        first.GetStratumDifferentiaBitWidth()
        == second.GetStratumDifferentiaBitWidth()
    )
    assert (
        calc_min_implausible_spurious_consecutive_differentia_collisions_between(
            first,
            second,
            significance_level=1.0 - confidence_level,
        )
        == 1
    )
    return calc_rank_of_first_retained_disparity_between(
        first,
        second,
        confidence_level=confidence_level,
    )
