import typing

from ..genome_instrumentation import HereditaryStratigraphicColumn
from ._calc_rank_of_first_retained_disparity_between import (
    calc_rank_of_first_retained_disparity_between,
)


def calc_definitive_max_rank_of_first_retained_disparity_between(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
) -> typing.Optional[int]:
    """Determine hard, exclusive upper bound on MRCA generation.

    At most, how many depositions elapsed along the columns' lines of
    descent before the first mismatching strata at the same rank between
    self and other?

    Returns
    -------
    int, optional
        The number of depositions elapsed or None if no disparity (i.e.,
        both columns have same number of strata deposited and the most
        recent stratum is common between self and other).

    Notes
    -----
    If no mismatching strata are found but self and other have different
    numbers of strata deposited, this method returns one greater than the
    lesser of the columns' deposition counts.
    """
    confidence_level = 0.49
    assert (
        self.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - confidence_level,
        )
        == 1
    )
    return self.CalcRankOfFirstRetainedDisparityWith(
        other,
        confidence_level=confidence_level,
    )
