import typing

from ..._detail import PolicyCouplerBase
from .._PolicySpec import PolicySpec
from .._impl import calc_provided_uncertainty


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

        if index == 0:
            # 0th index is always rank 0
            return 0
        elif (
            index
            == policy.CalcNumStrataRetainedExact(num_strata_deposited) - 1
        ):
            # case where index is the very most recent stratum
            return num_strata_deposited - 1
        elif index == policy.CalcNumStrataRetainedExact(num_strata_deposited):
            # in cases where the index is an in-progress
            # deposition rank must be calculated as the rank succeeding the
            # previous stratum's rank
            return (
                self(
                    policy,
                    index - 1,
                    num_strata_deposited,
                )
                + 1
            )
        else:
            # assumes no in-progress stratum depositions that haven't been
            # reflected in num_strata_deposited
            provided_uncertainty = calc_provided_uncertainty(
                spec.GetDepthProportionalResolution(),
                num_strata_deposited,
            )
            return min(index * provided_uncertainty, num_strata_deposited - 1)
