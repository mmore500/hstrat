from ..._auxiliary_lib import HereditaryStratigraphicArtifact
from ._calc_rank_of_mrca_bounds_provided_confidence_level import (
    calc_rank_of_mrca_bounds_provided_confidence_level,
)


def calc_ranks_since_mrca_bounds_provided_confidence_level(
    focal: HereditaryStratigraphicArtifact,
    other: HereditaryStratigraphicArtifact,
    prior: str,
    requested_confidence_level: float = 0.95,
) -> float:
    """Calculate provided confidence for a MRCA generation estimate.

    With what actual confidence is the true rank of the MRCA captured within the calculated estimate bounds for a requested confidence level?
    Guaranteed greater than or equal to the requested confidence level.

    The same argument may be provided for focal and other.
    """
    return calc_rank_of_mrca_bounds_provided_confidence_level(
        focal,
        other,
        prior,
        requested_confidence_level,
    )
