import typing

from ..genome_instrumentation import (
    HereditaryStratigraphicColumn,
    HereditaryStratumOrderedStoreDict,
    HereditaryStratumOrderedStoreList,
)
from ._impl import (
    calc_rank_of_first_retained_disparity_between_bsearch,
    calc_rank_of_first_retained_disparity_between_generic,
)


def calc_rank_of_first_retained_disparity_between(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    confidence_level: float = 0.95,
) -> typing.Optional[int]:
    """Determine upper bound on MRCA generation at given confidence.

    How many depositions elapsed along the columns' lines of
    descent before the first mismatching strata at the same rank between
    first and second?

    Parameters
    ----------
    confidence_level : float, optional
        With what probability should the true rank of the first disparity
        between first and second fall at or after the returned rank? Default
        0.95.

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

    The true rank of the first disparity with second is guaranteed to never
    be after the returned rank when confidence_level < 0.5.

    If the differentia width and confidence level are configured such that
    one or more suprious differentia collisions is plausible, this method
    will never return None.

    Consider two columns that compare identical at all common ranks. If
    these columns have few enough common ranks that all these collisions
    could plausibly be spurious then there is not yet enough to support
    common lineage between the columns so rank 0 must be selected as the
    estimated site of first retained disparity. If these columns have
    enough common ranks that all collisions could not plausibly be spurious
    then the largest rank that could not conceivably be spurious must be
    selected (and we are guaranteed such a rank exists). It is only when
    not even one collision could plausibly be spurious that strong enough
    evidence exists to conclude that there is no disparity.

    For example, the method may return None with 64-bit differentia and 95%
    confidence level but will never return None with 1-bit differentia and
    95% confidence level.
    """
    assert 0.0 <= confidence_level <= 1.0

    if (
        first.HasDiscardedStrata()
        or second.HasDiscardedStrata()
        # for performance reasons
        # only apply binary search to stores that support random access
        or not isinstance(
            first._stratum_ordered_store, HereditaryStratumOrderedStoreList
        )
        or not isinstance(
            second._stratum_ordered_store, HereditaryStratumOrderedStoreList
        )
        # binary search currently requires no spurious collisions
        or first.GetStratumDifferentiaBitWidth() < 64
    ):
        return calc_rank_of_first_retained_disparity_between_generic(
            first,
            second,
            confidence_level=confidence_level,
        )
    else:
        return calc_rank_of_first_retained_disparity_between_bsearch(
            first,
            second,
            confidence_level=confidence_level,
        )
