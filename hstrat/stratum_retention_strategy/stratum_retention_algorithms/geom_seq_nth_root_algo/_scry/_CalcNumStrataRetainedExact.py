import typing

from ..._detail import PolicyCouplerBase
from .._PolicySpec import PolicySpec
from .._impl import get_retained_ranks


class CalcNumStrataRetainedExact:
    """Functor to provide member function implementation in Policy class."""

    def __init__(
        self: "CalcNumStrataRetainedExact",
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        pass

    def __eq__(self: "CalcNumStrataRetainedExact", other: typing.Any) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "CalcNumStrataRetainedExact",
        policy: PolicyCouplerBase,
        num_strata_deposited: int,
    ) -> int:
        """Exactly how many strata are retained after n deposited?"""
        spec = policy.GetSpec()
        return len(
            get_retained_ranks(
                spec.GetDegree(),
                spec.GetInterspersal(),
                num_strata_deposited,
            )
        )
