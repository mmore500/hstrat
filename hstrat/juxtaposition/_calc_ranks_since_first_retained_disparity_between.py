import typing

from ..genome_instrumentation import HereditaryStratigraphicColumn
from ._calc_rank_of_first_retained_disparity_between import (
    calc_rank_of_first_retained_disparity_between,
)


def calc_ranks_since_first_retained_disparity_between(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    confidence_level: float = 0.95,
) -> typing.Optional[int]:
    """Determine generations since divergence with particular confidence.

    How many depositions have elapsed along this column's line of
    descent since the first mismatching strata at the same rank between
    self and other?

    Returns
    -------
    int, optional
        The number of depositions elapsed or None if no disparity (i.e.,
        both columns have same number of strata deposited and the most
        recent stratum is common between self and other).

    Parameters
    ----------
    confidence_level : float, optional
        With what probability should the true number of ranks since the
        first disparity be less than or equal to the returned estimate?
        Default 0.95.

    Notes
    -----
    Returns -1 if self and other share no mismatching strata at common
    ranks but other has more strata deposited then self.

    The true number of ranks since the first disparity with other is
    guaranteed strictly less than or equal to the returned estimate when
    confidence_level < 0.5.
    """
    first_disparate_rank = self.CalcRankOfFirstRetainedDisparityWith(
        other,
        confidence_level=confidence_level,
    )
    if first_disparate_rank is None:
        return None
    else:
        assert self.GetNumStrataDeposited()
        res = self.GetNumStrataDeposited() - 1 - first_disparate_rank
        assert -1 <= res < self.GetNumStrataDeposited()
        return res
