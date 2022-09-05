import typing

from ...genome_instrumentation import HereditaryStratigraphicColumn
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
    special case where both self and other use the perfect resolution
    stratum retention policy.
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

    collision_implausibility_threshold = (
        self.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - confidence_level,
        )
    )
    assert collision_implausibility_threshold > 0
    if first_disparite_idx is None:
        # no disparate strata found
        # fall back to _do_generic_CalcRankOfLastRetainedCommonalityWith
        # to handle proper bookkeeping in this case while skipping most of
        # the search
        return self._do_generic_CalcRankOfLastRetainedCommonalityWith(
            other,
            self_start_idx=upper_bound,
            other_start_idx=upper_bound,
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
        last_common_rank = self.GetRankAtColumnIndex(
            last_common_idx,
        )
        assert last_common_idx == last_common_rank
        return last_common_rank
    else:
        # no common strata between self and other
        # or not enough common strata to discount the possibility all
        # are spurious collisions with respect to the given confidence
        # level; conservatively conclude there is no common ancestor
        return None
