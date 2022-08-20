import typing

from ..._detail import PolicyCouplerBase
from .._PolicySpec import PolicySpec


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
        policy: typing.Optional[PolicyCouplerBase],
        first_num_strata_deposited: typing.Optional[int],
        second_num_strata_deposited: typing.Optional[int],
        actual_rank_of_mrca: typing.Optional[int],
    ) -> int:
        """Exactly how much uncertainty to estimate rank of MRCA?"""
        return 0
