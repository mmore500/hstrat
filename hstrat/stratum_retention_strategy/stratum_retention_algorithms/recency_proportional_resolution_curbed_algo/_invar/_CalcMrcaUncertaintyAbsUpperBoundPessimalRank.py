import typing

from ..._detail import PolicyCouplerBase
from .._PolicySpec import PolicySpec
from .._impl import pick_policy


class CalcMrcaUncertaintyAbsUpperBoundPessimalRank:
    """Functor to provide member function implementation in Policy class."""

    def __init__(
        self: "CalcMrcaUncertaintyAbsUpperBoundPessimalRank",
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        pass

    def __eq__(
        self: "CalcMrcaUncertaintyAbsUpperBoundPessimalRank",
        other: typing.Any,
    ) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "CalcMrcaUncertaintyAbsUpperBoundPessimalRank",
        policy: PolicyCouplerBase,
        first_num_strata_deposited: typing.Optional[int],
        second_num_strata_deposited: typing.Optional[int],
    ) -> int:
        """Calculate rank for which upper bound on absolute MRCA uncertainty is
        pessimized."""
        return pick_policy(
            policy.GetSpec().GetSizeCurb(),
            max(first_num_strata_deposited, second_num_strata_deposited),
        ).CalcMrcaUncertaintyAbsUpperBoundPessimalRank(
            first_num_strata_deposited, second_num_strata_deposited
        )
