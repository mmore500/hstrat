import math
import typing

from ..._detail import PolicyCouplerBase
from ..._impl import CalcMrcaUncertaintyAbsUpperBoundWorstCase
from .._PolicySpec import PolicySpec
from .._impl import calc_common_ratio


class CalcMrcaUncertaintyAbsUpperBound:
    """Functor to provide member function implementation in Policy class."""

    def __init__(
        self: "CalcMrcaUncertaintyAbsUpperBound",
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        pass

    def __eq__(
        self: "CalcMrcaUncertaintyAbsUpperBound",
        other: typing.Any,
    ) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "CalcMrcaUncertaintyAbsUpperBound",
        policy: PolicyCouplerBase,
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
        actual_rank_of_mrca: int,
    ) -> int:
        """At most, how much relative uncertainty to estimate rank of MRCA?
        Inclusive."""
        # rectify negative-indexed actual_rank_of_mrca
        if actual_rank_of_mrca is not None and actual_rank_of_mrca < 0:
            least_last_rank = min(
                first_num_strata_deposited - 1,
                second_num_strata_deposited - 1,
            )
            actual_rank_of_mrca += least_last_rank
            assert actual_rank_of_mrca >= 0

        spec = policy.GetSpec()

        max_num_strata_deposited = max(
            first_num_strata_deposited,
            second_num_strata_deposited,
        )
        if max_num_strata_deposited == 0:
            return 0

        interspersal = spec.GetInterspersal()
        # edge case: no uncertainty guarantee for interspersal 1
        # interspersal >= 2 required for uncertainty guarantee
        if interspersal == 1:
            return max_num_strata_deposited

        max_ranks_since_mrca = max_num_strata_deposited - actual_rank_of_mrca
        # edge case: columns are identical
        if max_ranks_since_mrca == 0:
            return 0

        common_ratio = calc_common_ratio(
            spec.GetDegree(), max_num_strata_deposited
        )
        # edge case: no strata have yet been dropped
        if common_ratio == 1.0:
            return 0

        # round up to next power of common_ratio
        rounded_ranks_since_mrca = common_ratio ** int(
            math.ceil(math.log(max_ranks_since_mrca, common_ratio))
        )
        # should be leq just multiplying max_ranks_since_mrca by common_ratio
        assert (
            rounded_ranks_since_mrca <= max_ranks_since_mrca * common_ratio
            # account for representation error etc.
            or math.isclose(
                rounded_ranks_since_mrca,
                max_ranks_since_mrca * common_ratio,
            )
        )

        # account for increased resolution from interspersal
        res = int(math.ceil(rounded_ranks_since_mrca / (interspersal - 1)))

        return min(
            res,
            CalcMrcaUncertaintyAbsUpperBoundWorstCase()(
                policy,
                first_num_strata_deposited,
                second_num_strata_deposited,
                actual_rank_of_mrca,
            ),
        )
