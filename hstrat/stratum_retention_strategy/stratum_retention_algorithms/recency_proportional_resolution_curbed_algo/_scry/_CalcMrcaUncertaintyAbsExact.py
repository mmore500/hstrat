import typing

from ..._detail import PolicyCouplerBase
from .._PolicySpec import PolicySpec
from .._impl import pick_policy


class CalcMrcaUncertaintyAbsExact:
    """Functor to provide member function implementation in Policy class."""

    def __init__(
        self: "CalcMrcaUncertaintyAbsExact",
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        pass

    def __eq__(self: "CalcMrcaUncertaintyAbsExact", other: typing.Any) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "CalcMrcaUncertaintyAbsExact",
        policy: PolicyCouplerBase,
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
        actual_rank_of_mrca: int,
    ) -> int:
        """Exactly how much uncertainty to estimate rank of MRCA?"""
        return pick_policy(
            policy.GetSpec()._size_curb,
            max(
                first_num_strata_deposited,
                second_num_strata_deposited,
            ),
        ).CalcMrcaUncertaintyAbsExact(
            first_num_strata_deposited,
            second_num_strata_deposited,
            actual_rank_of_mrca,
        )
