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

    def _CalcRankAtColumnIndexImpl(
        self: "CalcRankAtColumnIndex",
        policy: PolicyCouplerBase,
        index: int,
        num_strata_deposited: int,
    ) -> int:
        """After n strata have been deposited, what will the rank of the
        stratum at column index k be?

        Assumes that no in-progress stratum depositions that haven't been
        reflected in num_strata_deposited.
        """
        spec = policy.GetSpec()
        guaranteed_resolution = spec.GetDepthProportionalResolution()

        cur_stage_uncertainty = calc_provided_uncertainty(
            guaranteed_resolution,
            num_strata_deposited,
        )

        prev_stage_uncertainty = cur_stage_uncertainty // 2
        prev_stage_max_idx = (
            num_strata_deposited - 2
        ) // prev_stage_uncertainty

        thresh_idx = (
            2 * prev_stage_max_idx - 4 * guaranteed_resolution + 2
        ) // 2

        before_thresh_idx = min(thresh_idx, index)
        after_thresh_idx = max(index - thresh_idx, 0)

        return (
            before_thresh_idx * cur_stage_uncertainty
            + after_thresh_idx * prev_stage_uncertainty
        )

    def __call__(
        self: "CalcRankAtColumnIndex",
        policy: typing.Optional[PolicyCouplerBase],
        index: int,
        num_strata_deposited: typing.Optional[int],
    ) -> int:
        """After n strata have been deposited, what will the rank of the
        stratum at column index k be?

        Enables a HereditaryStratigraphicColumn using this predicate to
        optimize away storage of rank annotations on strata. Takes into the
        account the possibility for in-progress stratum depositions that haven't
        been reflected in num_strata_deposited.
        """
        spec = policy.GetSpec()
        guaranteed_resolution = spec.GetDepthProportionalResolution()

        if num_strata_deposited < guaranteed_resolution * 2 + 1:
            # use identity mapping before first ranks are condemned
            return index
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
            return self._CalcRankAtColumnIndexImpl(
                policy,
                index,
                num_strata_deposited,
            )
