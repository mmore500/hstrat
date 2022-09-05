import typing

from ..genome_instrumentation import HereditaryStratigraphicColumn
from ._calc_ranks_since_last_retained_commonality_between import (
    calc_ranks_since_last_retained_commonality_between,
)


def calc_definitive_min_ranks_since_last_retained_commonality_between(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
) -> typing.Optional[int]:
    """Determine hard, inclusive lower bound on generations since MRCA.

    At least, how many depositions have elapsed along this column's line of
    descent since the last matching strata at the same rank between self
    and other?

    Returns None if no common ancestor between self and other can be
    resolved with absolute confidence.
    """
    confidence_level = 0.49
    assert (
        self.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - confidence_level,
        )
        == 1
    )
    return self.CalcRanksSinceLastRetainedCommonalityWith(
        self,
        confidence_level=confidence_level,
    )
