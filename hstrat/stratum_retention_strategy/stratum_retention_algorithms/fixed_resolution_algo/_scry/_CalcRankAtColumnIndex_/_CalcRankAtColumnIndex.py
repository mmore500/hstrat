import typing

from ...._detail import PolicyCouplerBase
from ..._PolicySpec import PolicySpec


class CalcRankAtColumnIndex:
    """Functor to provide member function implementation in Policy class."""

    def __init__(
        self: "CalcRankAtColumnIndex",
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        pass

    def __eq__(self: "CalcRankAtColumnIndex", other: typing.Any) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "CalcRankAtColumnIndex",
        policy: PolicyCouplerBase,
        index: int,
        num_strata_deposited: int,
    ) -> int:
        """After n strata have been deposited, what will the rank of the
        stratum at column index k be?

        Enables a HereditaryStratigraphicColumn using this predicate to
        optimize away storage of rank annotations on strata. Takes into the
        account the possibility for in-progress stratum depositions that haven't
        been reflected in num_strata_deposited.
        """
        spec = policy.GetSpec()

        # upper bound implementation gives the exact number of strata retained
        if index == policy.CalcNumStrataRetainedExact(
            num_strata_deposited,
        ):
            # in-progress deposition case
            return num_strata_deposited
        else:
            return min(
                index * spec.GetFixedResolution(),
                num_strata_deposited - 1,
            )
