import typing

from ...genome_instrumentation import HereditaryStratigraphicColumn
from ._calc_rank_of_first_retained_disparity_between import (
    calc_rank_of_first_retained_disparity_between,
)
from ._calc_rank_of_last_retained_commonality_between import (
    calc_rank_of_last_retained_commonality_between,
)


def calc_rank_of_parity_segue_between(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    confidence_level_commonality: float,
    confidence_level_disparity: float,
) -> typing.Tuple[typing.Optional[int], typing.Optional[int]]:
    """Find last matching and first mismatching strata between columns.

    Implementation detail. Searches forward from index 0 for first mismatching
    retained differentiae between columns.
    """

    return (
        calc_rank_of_last_retained_commonality_between(
            first, second, confidence_level_commonality
        )
        if confidence_level_commonality is not None
        else None,
        calc_rank_of_first_retained_disparity_between(
            first, second, confidence_level_disparity
        )
        if confidence_level_disparity is not None
        else None,
    )
