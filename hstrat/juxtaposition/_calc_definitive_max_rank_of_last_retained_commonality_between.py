import typing

from ..genome_instrumentation import HereditaryStratigraphicColumn
from ._calc_rank_of_last_retained_commonality_between import (
    calc_rank_of_last_retained_commonality_between,
)


def calc_definitive_max_rank_of_last_retained_commonality_between(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
) -> typing.Optional[int]:
    """Determine latest possible generation of MRCA.

    At most, how many depositions elapsed along the columns' lines of
    descent before the last matching strata at the same rank between
    first and second?

    Returns
    -------
    int, optional
        The number of depositions elapsed or None if no common ancestor is
        shared between the columns.
    """
    confidence_level = 0.49
    assert (
        first.GetStratumDifferentiaBitWidth()
        == second.GetStratumDifferentiaBitWidth()
    )
    assert (
        first.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - confidence_level,
        )
        == 1
    )
    return calc_rank_of_last_retained_commonality_between(
        first,
        second,
        confidence_level=confidence_level,
    )
