import typing

from .._detail._PolicyCouplerBase import PolicyCouplerBase
from ._CalcMrcaUncertaintyAbsUpperBoundWorstCase import (
    CalcMrcaUncertaintyAbsUpperBoundWorstCase,
)


class CalcMrcaUncertaintyRelUpperBoundWorstCase:
    def __init__(
        self: "CalcMrcaUncertaintyRelUpperBoundWorstCase",
        policy_spec: typing.Optional[typing.Any] = None,
    ) -> None:
        pass

    def __eq__(
        self: "CalcMrcaUncertaintyRelUpperBoundWorstCase",
        other: typing.Any,
    ) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "CalcMrcaUncertaintyRelUpperBoundWorstCase",
        policy: typing.Optional[PolicyCouplerBase],
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
        actual_rank_of_mrca: int,
    ) -> float:
        """At most, how much uncertainty to relative estimate rank of MRCA?
        Inclusive."""
        # rectify negative-indexed actual_rank_of_mrca
        if actual_rank_of_mrca is not None and actual_rank_of_mrca < 0:
            least_last_rank = min(
                first_num_strata_deposited - 1,
                second_num_strata_deposited - 1,
            )
            actual_rank_of_mrca += least_last_rank
            assert actual_rank_of_mrca >= 0

        if 0 in (first_num_strata_deposited, second_num_strata_deposited):
            return 0.0

        least_last_rank = min(
            first_num_strata_deposited - 1,
            second_num_strata_deposited - 1,
        )

        # conservatively normalize by smallest ranks since mrca
        min_ranks_since_mrca = least_last_rank - actual_rank_of_mrca
        worst_abs_uncertainty = CalcMrcaUncertaintyAbsUpperBoundWorstCase()(
            policy,
            first_num_strata_deposited,
            second_num_strata_deposited,
            actual_rank_of_mrca,
        )

        if min_ranks_since_mrca == 0:
            return 0.0
        else:
            return worst_abs_uncertainty / min_ranks_since_mrca
