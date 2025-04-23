import typing

import opytional as opyt

from ..._auxiliary_lib import HereditaryStratigraphicArtifact
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
    first: HereditaryStratigraphicArtifact,
    second: HereditaryStratigraphicArtifact,
    confidence_level: float,
) -> typing.Optional[int]:
    """Find first mismatching strata between columns.

    Implementation detail. Provides optimized implementation for special
    case where both self and second use the perfect resolution stratum
    retention policy.
    """

    impl = (
        calc_rank_of_first_retained_disparity_between_generic
        if (
            not isinstance(first, HereditaryStratigraphicColumn)
            or not isinstance(second, HereditaryStratigraphicColumn)
            or first.HasDiscardedStrata()
            or second.HasDiscardedStrata()
            # for performance reasons
            # only apply binary search to stores that support random access
            or not hasattr(first, "_stratum_ordered_store")
            or not isinstance(
                first._stratum_ordered_store, HereditaryStratumOrderedStoreList
            )
            or not hasattr(second, "_stratum_ordered_store")
            or not isinstance(
                second._stratum_ordered_store,
                HereditaryStratumOrderedStoreList,
            )
            # binary search currently requires no spurious collisions
            or first.GetStratumDifferentiaBitWidth() < 64
        )
        else calc_rank_of_first_retained_disparity_between_bsearch
    )

    res = impl(first, second, confidence_level=confidence_level)
    res = opyt.apply_if(res, lambda x: max(x, 0))  # handle negative rank case
    return res
