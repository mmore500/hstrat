import typing

from ..._detail import PolicyCouplerBase
from ..._impl import CalcMrcaUncertaintyRelUpperBoundWorstCase
from .._PolicySpec import PolicySpec
from .._impl import calc_common_ratio


class CalcMrcaUncertaintyRelUpperBound:
    """Functor to provide member function implementation in Policy class."""

    def __init__(
        self: "CalcMrcaUncertaintyRelUpperBound",
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        pass

    def __eq__(
        self: "CalcMrcaUncertaintyRelUpperBound",
        other: typing.Any,
    ) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "CalcMrcaUncertaintyRelUpperBound",
        policy: PolicyCouplerBase,
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
        actual_rank_of_mrca: int,
    ) -> float:
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

        interspersal = spec.GetInterspersal()
        # edge case: no uncertainty guarantee for interspersal 1
        # interspersal >= 2 required for uncertainty guarantee
        if interspersal == 1:
            return CalcMrcaUncertaintyRelUpperBoundWorstCase()(
                policy,
                first_num_strata_deposited,
                second_num_strata_deposited,
                actual_rank_of_mrca,
            )

        if 0 in (first_num_strata_deposited, second_num_strata_deposited):
            return 0.0

        min_num_strata_deposited, max_num_strata_deposited = sorted(
            [
                first_num_strata_deposited,
                second_num_strata_deposited,
            ]
        )

        length_ratio = max_num_strata_deposited / min_num_strata_deposited

        common_ratio = calc_common_ratio(
            spec.GetDegree(), max_num_strata_deposited
        )

        res = length_ratio * common_ratio / (interspersal - 1)

        # tighten to worst-possible case given number of strata deposited
        return min(
            res,
            CalcMrcaUncertaintyRelUpperBoundWorstCase()(
                policy,
                first_num_strata_deposited,
                second_num_strata_deposited,
                actual_rank_of_mrca,
            ),
        )
