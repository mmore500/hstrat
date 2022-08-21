import typing

from .._detail._PolicyCouplerBase import PolicyCouplerBase


class CalcMrcaUncertaintyAbsUpperBoundWorstCase:
    def __init__(
        self: "CalcMrcaUncertaintyAbsUpperBoundWorstCase",
        policy_spec: typing.Optional[typing.Any] = None,
    ) -> None:
        pass

    def __eq__(
        self: "CalcMrcaUncertaintyAbsUpperBoundWorstCase",
        other: typing.Any,
    ) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "CalcMrcaUncertaintyAbsUpperBoundWorstCase",
        policy: typing.Optional[PolicyCouplerBase],
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
        actual_rank_of_mrca: int,
    ) -> int:
        """At most, how much absolute uncertainty to estimate rank of MRCA?
        Inclusive."""
        # rectify negative-indexed actual_rank_of_mrca
        if actual_rank_of_mrca is not None and actual_rank_of_mrca < 0:
            least_last_rank = min(
                first_num_strata_deposited - 1,
                second_num_strata_deposited - 1,
            )
            actual_rank_of_mrca += least_last_rank
            assert actual_rank_of_mrca >= 0

        # assumes (required) retention of rank 0 and last rank
        least_num_strata_deposited = min(
            first_num_strata_deposited,
            second_num_strata_deposited,
        )
        if actual_rank_of_mrca == least_num_strata_deposited - 1:
            return 0
        else:
            return max(least_num_strata_deposited - 2, 0)
