import typing

from ...genome_instrumentation import (
    HereditaryStratigraphicColumn,
    HereditaryStratumOrderedStoreList,
)
from ._calc_rank_of_first_retained_disparity_between_bsearch import (
    calc_rank_of_first_retained_disparity_between_bsearch,
)
from ._calc_rank_of_first_retained_disparity_between_generic import (
    calc_rank_of_first_retained_disparity_between_generic,
)


def calc_rank_of_first_retained_disparity_between(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    confidence_level: float,
) -> typing.Optional[int]:
    """Find first mismatching strata between columns.

    Implementation detail. Provides optimized implementation for special
    case where both self and second use the perfect resolution stratum
    retention policy.
    """

    if (
        first.HasDiscardedStrata()
        or second.HasDiscardedStrata()
        # for performance reasons
        # only apply binary search to stores that support random access
        or not hasattr(first, "_stratum_ordered_store")
        or not isinstance(
            first._stratum_ordered_store, HereditaryStratumOrderedStoreList
        )
        or not hasattr(second, "_stratum_ordered_store")
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
