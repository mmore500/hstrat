import typing

from .._detail._PolicyCouplerBase import PolicyCouplerBase


class CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank:
    def __init__(
        self: "CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank",
        policy_spec: typing.Optional[typing.Any] = None,
    ) -> None:
        pass

    def __eq__(
        self: "CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank",
        other: typing.Any,
    ) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank",
        policy: PolicyCouplerBase,
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
    ) -> int:
        """Calculate absolute MRCA uncertainty at pessimal rank."""
        pessimal_rank = policy.CalcMrcaUncertaintyAbsUpperBoundPessimalRank(
            first_num_strata_deposited,
            second_num_strata_deposited,
        )

        return policy.CalcMrcaUncertaintyAbsUpperBound(
            first_num_strata_deposited,
            second_num_strata_deposited,
            pessimal_rank,
        )
