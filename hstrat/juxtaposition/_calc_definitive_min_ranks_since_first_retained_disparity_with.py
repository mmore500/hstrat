import typing

from .._auxiliary_lib import HereditaryStratigraphicArtifact
from ._calc_min_implausible_spurious_consecutive_differentia_collisions_between import (
    calc_min_implausible_spurious_consecutive_differentia_collisions_between,
)
from ._calc_ranks_since_first_retained_disparity_with import (
    calc_ranks_since_first_retained_disparity_with,
)


def calc_definitive_min_ranks_since_first_retained_disparity_with(
    focal: HereditaryStratigraphicArtifact,
    other: HereditaryStratigraphicArtifact,
) -> typing.Optional[int]:
    """Determine a hard, exclusive lower bound on generations since MRCA.

    At least, how many depositions have elapsed along the focal column's line
    of descent since the first mismatching strata at the same rank between
    focal and other?

    Returns None if no disparity found (i.e., both columns have same number
    of strata deposited and the most recent stratum is common between focal
    and other).
    """
    confidence_level = 0.49
    assert (
        focal.GetStratumDifferentiaBitWidth()
        == other.GetStratumDifferentiaBitWidth()
    )
    assert (
        calc_min_implausible_spurious_consecutive_differentia_collisions_between(
            focal,
            other,
            significance_level=1.0 - confidence_level,
        )
        == 1
    )
    return calc_ranks_since_first_retained_disparity_with(
        focal,
        other,
        confidence_level=confidence_level,
    )
