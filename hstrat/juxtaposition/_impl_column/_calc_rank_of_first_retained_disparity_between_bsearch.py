import typing

from interval_search import binary_search

from ...genome_instrumentation import HereditaryStratigraphicColumn
from .._calc_min_implausible_spurious_consecutive_differentia_collisions_between import (
    calc_min_implausible_spurious_consecutive_differentia_collisions_between,
)
from ._calc_rank_of_first_retained_disparity_between_generic import (
    calc_rank_of_first_retained_disparity_between_generic,
)


def calc_rank_of_first_retained_disparity_between_bsearch(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    confidence_level: float,
) -> typing.Optional[int]:
    """Find first mismatching strata between columns.

    Implementation detail. Provides optimized implementation for special
    case where both self and second use the perfect resolution stratum
    retention policy.
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

    if first_disparite_idx is not None:
        # disparate strata found
        assert (
            first.GetStratumDifferentiaBitWidth()
            == second.GetStratumDifferentiaBitWidth()
        )
        collision_plausibility_threshold = (
            calc_min_implausible_spurious_consecutive_differentia_collisions_between(
                first,
                second,
                significance_level=1.0 - confidence_level,
            )
            - 1
        )
        # discount collision_implausibility_threshold - 1 common
        # ranks due to potential spurious differentia collisions;
        # if not enough common ranks are available we still know
        # *definitively* that a disparity occured (because we
        # observed disparite strata at the same rank); so, make the
        # conservative assumption that the disparity occured as far
        # back as possible (rank 0)
        spurious_collision_corrected_idx = max(
            first_disparite_idx - collision_plausibility_threshold,
            0,
        )
        first_disparite_rank = first.GetRankAtColumnIndex(
            spurious_collision_corrected_idx
        )
        assert first_disparite_rank >= 0
        return first_disparite_rank
    else:
        # no disparate strata found
        # fall back to calc_rank_of_first_retained_disparity_between_generic to
        # handle proper bookkeeping in this case while skipping most of the
        # search
        return calc_rank_of_first_retained_disparity_between_generic(
            first,
            second,
            first_start_idx=upper_bound,
            second_start_idx=upper_bound,
            confidence_level=confidence_level,
        )
