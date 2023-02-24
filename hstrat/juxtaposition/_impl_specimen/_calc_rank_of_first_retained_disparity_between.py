import typing

from ...frozen_instrumentation import HereditaryStratigraphicSpecimen
from ._calc_rank_of_parity_segue_between import (
    calc_rank_of_parity_segue_between,
)


def calc_rank_of_first_retained_disparity_between(
    first: HereditaryStratigraphicSpecimen,
    second: HereditaryStratigraphicSpecimen,
    confidence_level: float,
) -> typing.Optional[int]:
    """Find first mismatching strata between columns.

    Implementation detail. Provides optimized implementation for special
    case where both self and second use the perfect resolution stratum
    retention policy.
    """
    return calc_rank_of_parity_segue_between(
        first,
        second,
        None,
        confidence_level,
    )[1]
