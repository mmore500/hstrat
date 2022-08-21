import typing

from .._detail._PolicyCouplerBase import PolicyCouplerBase


class CalcNumStrataRetainedUpperBoundWorstCase:
    def __init__(
        self: "CalcNumStrataRetainedUpperBoundWorstCase",
        policy_spec: typing.Optional[typing.Any] = None,
    ) -> None:
        pass

    def __eq__(
        self: "CalcNumStrataRetainedUpperBoundWorstCase",
        other: typing.Any,
    ) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "CalcNumStrataRetainedUpperBoundWorstCase",
        policy: typing.Optional[PolicyCouplerBase],
        num_strata_deposited: int,
    ) -> int:
        """At most, how many strata are retained after n deposited? Inclusive."""
        return num_strata_deposited
