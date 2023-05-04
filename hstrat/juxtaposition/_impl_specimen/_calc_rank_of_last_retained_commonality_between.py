import typing

from ...frozen_instrumentation import HereditaryStratigraphicSpecimen
from ._calc_rank_of_parity_segue_between import (
    calc_rank_of_parity_segue_between,
)


def calc_rank_of_last_retained_commonality_between(
    first: HereditaryStratigraphicSpecimen,
    second: HereditaryStratigraphicSpecimen,
    confidence_level: float,
) -> typing.Optional[int]:
    """Find rank of strata commonality before first strata disparity.

    Implementation detail with general-case implementation.
    """
    return calc_rank_of_parity_segue_between(
        first,
        second,
        confidence_level,
        None,
    )[0]
