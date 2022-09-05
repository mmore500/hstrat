import typing

from ...genome_instrumentation import HereditaryStratigraphicColumn
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
    case where both self and other use the perfect resolution stratum
    retention policy.
    """
    # both must have (effectively) used the perfect resolution policy
    assert not self.HasDiscardedStrata() and not other.HasDiscardedStrata()

    lower_bound = 0
    upper_bound = min(
        [
            self.GetNumStrataDeposited() - 1,
            other.GetNumStrataDeposited() - 1,
        ]
    )
    assert lower_bound <= upper_bound

    def differentia_at(
        which: HereditaryStratigraphicColumn,
        idx: int,
    ) -> int:
        return which.GetStratumAtColumnIndex(idx).GetDifferentia()

    def predicate(idx: int) -> bool:
        return differentia_at(self, idx) != differentia_at(other, idx)

    first_disparite_idx = binary_search(
        predicate,
        lower_bound,
        upper_bound,
    )

    if first_disparite_idx is not None:
        # disparate strata found
        collision_plausibility_threshold = (
            self.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
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
        first_disparite_rank = self.GetRankAtColumnIndex(
            spurious_collision_corrected_idx
        )
        return first_disparite_rank
    else:
        # no disparate strata found
        # fall back to _do_generic_CalcRankOfFirstRetainedDisparityWith to
        # handle proper bookkeeping in this case while skipping most of the
        # search
        return self._do_generic_CalcRankOfFirstRetainedDisparityWith(
            other,
            self_start_idx=upper_bound,
            other_start_idx=upper_bound,
            confidence_level=confidence_level,
        )
