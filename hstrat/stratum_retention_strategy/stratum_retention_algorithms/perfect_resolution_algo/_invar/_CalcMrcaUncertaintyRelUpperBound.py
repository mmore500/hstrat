import typing

from ..._detail import PolicyCouplerBase
from .._PolicySpec import PolicySpec


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
        policy: typing.Optional[PolicyCouplerBase],
        first_num_strata_deposited: typing.Optional[int],
        second_num_strata_deposited: typing.Optional[int],
        actual_rank_of_mrca: typing.Optional[int],
    ) -> float:
        """At most, how much relative uncertainty to estimate rank of MRCA?
        Inclusive."""
        return 0.0
