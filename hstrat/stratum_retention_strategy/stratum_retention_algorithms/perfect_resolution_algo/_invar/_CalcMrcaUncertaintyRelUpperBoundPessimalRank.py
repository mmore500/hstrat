import typing

from ..._detail import PolicyCouplerBase
from .._PolicySpec import PolicySpec


class CalcMrcaUncertaintyRelUpperBoundPessimalRank:
    """Functor to provide member function implementation in Policy class."""

    def __init__(
        self: "CalcMrcaUncertaintyRelUpperBoundPessimalRank",
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        pass

    def __eq__(
        self: "CalcMrcaUncertaintyRelUpperBoundPessimalRank",
        other: typing.Any,
    ) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "CalcMrcaUncertaintyRelUpperBoundPessimalRank",
        policy: PolicyCouplerBase,
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
    ) -> int:
        """Calculate rank for which upper bound on relative MRCA uncertainty is
        pessimized."""
        return 0
