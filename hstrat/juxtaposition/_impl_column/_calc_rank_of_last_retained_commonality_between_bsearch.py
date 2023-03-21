import typing

from interval_search import binary_search

from ...genome_instrumentation import HereditaryStratigraphicColumn
from .._calc_min_implausible_spurious_consecutive_differentia_collisions_between import (
    calc_min_implausible_spurious_consecutive_differentia_collisions_between,
)
from ._calc_rank_of_last_retained_commonality_between_generic import (
    calc_rank_of_last_retained_commonality_between_generic,
)


def calc_rank_of_last_retained_commonality_between_bsearch(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    confidence_level: float,
) -> typing.Optional[int]:
    """Find rank of strata commonality before first strata disparity.

    Implementation detail. Provides optimized implementation for
    special case where both first and second use the perfect resolution
    stratum retention policy.
    """
    # both must have (effectively) used the perfect resolution policy
    assert not first.HasDiscardedStrata() and not second.HasDiscardedStrata()

    lower_bound = 0
    upper_bound = min(
        [
            first.GetNumStrataDeposited() - 1,
            second.GetNumStrataDeposited() - 1,
        ]
    )
    assert lower_bound <= upper_bound

    def differentia_at(
        which: HereditaryStratigraphicColumn,
        idx: int,
    ) -> int:
        return which.GetStratumAtColumnIndex(idx).GetDifferentia()

    def predicate(idx: int) -> bool:
        return differentia_at(first, idx) != differentia_at(second, idx)

    first_disparite_idx = binary_search(
        predicate,
        lower_bound,
        upper_bound,
    )

    collision_implausibility_threshold = calc_min_implausible_spurious_consecutive_differentia_collisions_between(
        first,
        second,
        significance_level=1.0 - confidence_level,
    )
    assert collision_implausibility_threshold > 0
    if first_disparite_idx is None:
        # no disparate strata found
        # fall back to calc_rank_of_last_retained_commonality_between_generic
        # to handle proper bookkeeping in this case while skipping most of
        # the search
        return calc_rank_of_last_retained_commonality_between_generic(
            first,
            second,
            first_start_idx=upper_bound,
            second_start_idx=upper_bound,
            confidence_level=confidence_level,
        )
    elif first_disparite_idx >= collision_implausibility_threshold:
        # disparate strata found, following some common strata
        # ...discount collision_implausibility_threshold - 1 common strata
        # as potential spurious differentia collisions
        # ... must also subtract 1 (canceling out -1 above) to account for
        # moving from disparite stratum to preceding common stratum
        last_common_idx = (
            first_disparite_idx - collision_implausibility_threshold
        )
        last_common_rank = first.GetRankAtColumnIndex(
            last_common_idx,
        )
        assert last_common_idx == last_common_rank
        return last_common_rank
    else:
        # no common strata between first and second
        # or not enough common strata to discount the possibility all
        # are spurious collisions with respect to the given confidence
        # level; conservatively conclude there is no common ancestor
        return None
