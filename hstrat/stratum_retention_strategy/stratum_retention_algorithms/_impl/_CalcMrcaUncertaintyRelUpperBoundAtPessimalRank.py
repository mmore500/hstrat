import typing

from .._detail._PolicyCouplerBase import PolicyCouplerBase


class CalcMrcaUncertaintyRelUpperBoundAtPessimalRank:
    def __init__(
        self: "CalcMrcaUncertaintyRelUpperBoundAtPessimalRank",
        policy_spec: typing.Optional[typing.Any] = None,
    ) -> None:
        pass

    def __eq__(
        self: "CalcMrcaUncertaintyRelUpperBoundAtPessimalRank",
        other: typing.Any,
    ) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "CalcMrcaUncertaintyRelUpperBoundAtPessimalRank",
        policy: PolicyCouplerBase,
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
    ) -> float:
        """Calculate relative MRCA uncertainty at pessimal rank."""
        pessimal_rank = policy.CalcMrcaUncertaintyRelUpperBoundPessimalRank(
            first_num_strata_deposited,
            second_num_strata_deposited,
        )

        return policy.CalcMrcaUncertaintyRelUpperBound(
            first_num_strata_deposited,
            second_num_strata_deposited,
            pessimal_rank,
        )
