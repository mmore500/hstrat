import math

from .._auxiliary_lib import HereditaryStratigraphicArtifact
from ._calc_probability_differentia_collision_between import (
    calc_probability_differentia_collision_between,
)


def calc_min_implausible_spurious_consecutive_differentia_collisions_between(
    first: HereditaryStratigraphicArtifact,
    second: HereditaryStratigraphicArtifact,
    significance_level: float,
) -> int:
    """Determine amount of evidence required to indicate shared ancestry.

    Calculates how many differentia collisions are required to reject the
    null hypothesis that columns do not share common ancestry at those
    ranks at significance level significance_level.
    """
    assert 0.0 <= significance_level <= 1.0
    assert (
        first.GetStratumDifferentiaBitWidth()
        == second.GetStratumDifferentiaBitWidth()
    )

    if significance_level * first.GetStratumDifferentiaBitWidth() > 1:
        return 1

    log_base = calc_probability_differentia_collision_between(first, second)
    if significance_level >= log_base:
        return 1
    else:
        return int(math.ceil(math.log(significance_level, log_base)))
