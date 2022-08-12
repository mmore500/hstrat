import typing

from .._impl import calc_provided_uncertainty
from ..PolicySpec import PolicySpec

class CalcMrcaUncertaintyAbsExact:
    """Functor to provide member function implementation in Policy class."""

    def __init__(
        self: 'CalcMrcaUncertaintyAbsExact',
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        pass

    def __eq__(
        self: 'CalcMrcaUncertaintyAbsExact',
        other: typing.Any,
    ) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: 'CalcMrcaUncertaintyAbsExact',
        policy: 'Policy',
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
        actual_rank_of_mrca: int,
    ) -> int:
        """Exactly how much uncertainty to estimate rank of MRCA?"""

        spec = policy.GetSpec()

        least_num_strata_deposited = min(
            first_num_strata_deposited,
            second_num_strata_deposited,
        )
        least_last_rank = least_num_strata_deposited - 1

        uncertainty = calc_provided_uncertainty(
            spec._guaranteed_depth_proportional_resolution,
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
