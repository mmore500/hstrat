import typing

from ..._detail import PolicyCouplerBase
from .._PolicySpec import PolicySpec
from .._impl import calc_provided_uncertainty


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
        policy: PolicyCouplerBase,
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
        actual_rank_of_mrca: int,
    ) -> int:
        """Exactly how much uncertainty to estimate rank of MRCA?"""
        # rectify negative-indexed actual_rank_of_mrca
        if actual_rank_of_mrca is not None and actual_rank_of_mrca < 0:
            least_last_rank = min(
                first_num_strata_deposited - 1,
                second_num_strata_deposited - 1,
            )
            actual_rank_of_mrca += least_last_rank
            assert actual_rank_of_mrca >= 0

        spec = policy.GetSpec()
        guaranteed_resolution = spec.GetDepthProportionalResolution()

        least_num_strata_deposited = min(
            first_num_strata_deposited,
            second_num_strata_deposited,
        )
        least_last_rank = least_num_strata_deposited - 1

        # mrca at very last rank
        if actual_rank_of_mrca == least_last_rank:
            return 0
        # haven't added enough ranks to start dropping ranks
        elif least_last_rank < guaranteed_resolution * 2:
            return 0

        cur_stage_uncertainty = calc_provided_uncertainty(
            guaranteed_resolution,
            least_num_strata_deposited,
        )
        cur_stage_max_idx = (  # noqa: F841, keep unused for comprehensibility
            least_num_strata_deposited // cur_stage_uncertainty
        )

        prev_stage_uncertainty = cur_stage_uncertainty // 2
        prev_stage_max_idx = (least_last_rank - 1) // prev_stage_uncertainty

        thresh_idx = (
            2 * prev_stage_max_idx - 4 * guaranteed_resolution + 2
        ) // 2

        # note that cur stage uncertainty is iterated through first
        # because ranks are removed from the back, the old prev stage
        # uncertainty lingers at more recent ranks
        if actual_rank_of_mrca < thresh_idx * cur_stage_uncertainty:
            # mrca between last regularly-spaced rank and tail rank
            if actual_rank_of_mrca >= (
                least_last_rank - least_last_rank % cur_stage_uncertainty
            ):
                return (least_last_rank - 1) % cur_stage_uncertainty
            # mrca between two regularly-spaced ranks
            else:
                return cur_stage_uncertainty - 1
        # mrca between last regularly-spaced rank and tail rank
        elif actual_rank_of_mrca >= (
            least_last_rank - least_last_rank % prev_stage_uncertainty
        ):
            return (least_last_rank - 1) % prev_stage_uncertainty
        # mrca between two regularly-spaced ranks
        else:
            return prev_stage_uncertainty - 1
