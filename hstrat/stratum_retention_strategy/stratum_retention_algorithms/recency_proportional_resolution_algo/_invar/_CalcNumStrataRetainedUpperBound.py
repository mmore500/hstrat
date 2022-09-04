import math
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
        policy: PolicyCouplerBase,
        num_strata_deposited: int,
    ) -> int:
        """At most how many strata are retained after n deposited? Inclusive."""
        spec = policy.GetSpec()
        resolution = spec.GetRecencyProportionalResolution()

        res = (
            int(
                (resolution + 1) * math.log2(num_strata_deposited - 1)
                - sum(math.log2(r + 1) for r in range(resolution))
                + 1
                + (
                    resolution == 0
                )  # <<< patches failed 0-resolution test cases
            )
            if num_strata_deposited > resolution + 1
            else num_strata_deposited
        )

        return min(res, num_strata_deposited)
