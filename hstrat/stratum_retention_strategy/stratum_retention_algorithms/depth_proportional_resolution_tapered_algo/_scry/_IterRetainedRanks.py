import typing

from ..._detail import PolicyCouplerBase
from .._PolicySpec import PolicySpec
from .._impl import calc_provided_uncertainty


class IterRetainedRanks:
    """Functor to provide member function implementation in Policy class."""

    def __init__(
        self: "IterRetainedRanks",
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        pass

    def __eq__(self: "IterRetainedRanks", other: typing.Any) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "IterRetainedRanks",
        policy: PolicyCouplerBase,
        num_strata_deposited: int,
    ) -> typing.Iterator[int]:
        """Iterate over retained strata ranks at `num_strata_deposited` in
        ascending order."""
        spec = policy.GetSpec()
        guaranteed_resolution = spec.GetDepthProportionalResolution()

        if num_strata_deposited < guaranteed_resolution * 2 + 1:
            # use identity mapping before first ranks are condemned
            yield from range(num_strata_deposited)
            return

        cur_stage_uncertainty = calc_provided_uncertainty(
            guaranteed_resolution,
            num_strata_deposited,
        )
        cur_stage_max_idx = (  # noqa: F841, keep unused for comprehensibility
            num_strata_deposited // cur_stage_uncertainty
        )

        prev_stage_uncertainty = cur_stage_uncertainty // 2
        prev_stage_max_idx = (
            num_strata_deposited - 2
        ) // prev_stage_uncertainty
        thresh_idx = (
            2 * prev_stage_max_idx - 4 * guaranteed_resolution + 2
        ) // 2

        # note that cur stage uncertainty is iterated through first
        # because ranks are removed from the back, the old prev stage
        # uncertainty lingers at more recent ranks
        yield from range(
            0,
            thresh_idx * cur_stage_uncertainty,
            cur_stage_uncertainty,
        )
        yield from range(
            thresh_idx * cur_stage_uncertainty,
            num_strata_deposited,
            prev_stage_uncertainty,
        )

        last_rank = num_strata_deposited - 1
        if thresh_idx * cur_stage_uncertainty > last_rank:
            if last_rank > 0 and last_rank % cur_stage_uncertainty:
                yield last_rank
        elif last_rank > 0 and last_rank % prev_stage_uncertainty:
            yield last_rank
