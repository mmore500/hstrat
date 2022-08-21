import typing

from ..._detail import PolicyCouplerBase
from .._PolicySpec import PolicySpec


class CalcNumStrataRetainedUpperBound:
    """Functor to provide member function implementation in Policy class."""

    def __init__(
        self: "CalcNumStrataRetainedUpperBound",
        policy_spec: typing.Optional[PolicySpec] = None,
    ) -> None:
        pass

    def __eq__(
        self: "CalcNumStrataRetainedUpperBound",
        other: typing.Any,
    ) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "CalcNumStrataRetainedUpperBound",
        policy: typing.Optional[PolicyCouplerBase],
        num_strata_deposited: int,
    ) -> int:
        """At most, how many strata are retained after n deposited? Inclusive."""
        return min(2, num_strata_deposited)
