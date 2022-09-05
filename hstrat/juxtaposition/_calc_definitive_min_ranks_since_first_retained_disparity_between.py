import typing

from ..genome_instrumentation import HereditaryStratigraphicColumn
from ._calc_ranks_since_first_retained_disparity_between import (
    calc_ranks_since_first_retained_disparity_between,
)


def calc_definitive_min_ranks_since_first_retained_disparity_between(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
) -> typing.Optional[int]:
    """Determine a hard, exclusive lower bound on generations since MRCA.

    At least, how many depositions have elapsed along this column's line
    of descent since the first mismatching strata at the same rank between
    self and other?

    Returns None if no disparity found (i.e., both columns have same number
    of strata deposited and the most recent stratum is common between self
    and other).
    """
    confidence_level = 0.49
    assert (
        self.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - confidence_level,
        )
        == 1
    )
    return self.CalcRanksSinceFirstRetainedDisparityWith(
        other,
        confidence_level=confidence_level,
    )
