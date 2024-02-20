import typing

from ..._auxiliary_lib import HereditaryStratigraphicArtifact
from ...juxtaposition import (
    calc_min_implausible_spurious_consecutive_differentia_collisions_between,
    calc_probability_differentia_collision_between,
)


def calc_rank_of_mrca_bounds_provided_confidence_level(
    focal: HereditaryStratigraphicArtifact,
    other: HereditaryStratigraphicArtifact,
    prior: typing.Literal["arbitrary"],
    requested_confidence_level: float = 0.95,
) -> float:
    """Calculate provided confidence for a MRCA generation estimate.

    With what actual confidence is the true rank of the MRCA captured within the calculated estimate bounds for a requested confidence level?
    Guaranteed greater than or equal to the requested confidence level.

    The same argument may be provided for focal and other.
    """
    if prior != "arbitrary":
        raise NotImplementedError
    assert 0.0 <= requested_confidence_level <= 1.0
    if other is not None:
        assert (
            focal.GetStratumDifferentiaBitWidth()
            == other.GetStratumDifferentiaBitWidth()
        )

    n = calc_min_implausible_spurious_consecutive_differentia_collisions_between(
        focal,
        other,
        significance_level=1 - requested_confidence_level,
    )
    res = 1 - calc_probability_differentia_collision_between(focal, other) ** n
    assert res >= requested_confidence_level
    assert 0 <= res <= 1
    return res
