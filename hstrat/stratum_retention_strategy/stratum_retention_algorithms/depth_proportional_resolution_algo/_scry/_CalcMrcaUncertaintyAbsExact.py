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

        least_num_strata_deposited = min(
            first_num_strata_deposited,
            second_num_strata_deposited,
        )
        least_last_rank = least_num_strata_deposited - 1

        uncertainty = calc_provided_uncertainty(
            spec.GetDepthProportionalResolution(),
            least_num_strata_deposited,
        )

        # mrca at very last rank
        if actual_rank_of_mrca == least_last_rank:
            return 0
        # haven't added enough ranks to hit resolution
        elif least_last_rank < uncertainty:
            return least_last_rank - 1
        # mrca between last regularly-spaced rank and tail rank
        elif actual_rank_of_mrca >= (
            least_last_rank - least_last_rank % uncertainty
        ):
            return (least_last_rank - 1) % uncertainty
        # mrca between two regularly-spaced ranks
        else:
            return uncertainty - 1
