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
        resolution = spec.GetRecencyProportionalResolution()

        least_num_strata_deposited = min(
            first_num_strata_deposited,
            second_num_strata_deposited,
        )
        least_last_rank = least_num_strata_deposited - 1
        # mrca at very last rank
        if least_last_rank - actual_rank_of_mrca <= resolution:
            return 0

        provided_uncertainty = calc_provided_uncertainty(
            resolution,
            least_last_rank,
        )
        if provided_uncertainty == 1:
            return 0

        # we could just take a simple recursive approach like this
        #
        #   if index == 0: return 0
        #   else: return provided_uncertainty + self.CalcRankAtColumnIndex(
        #       index - 1,
        #       num_strata_deposited - provided_uncertainty,
        #   )
        #
        # but as an optimization, we should take as many steps as possible at
        # the current uncertainty interval size stage before recursing down to
        # the next half-as-small uncertainty interval size

        # calculate the greatest rank at which that interval is viable
        # i.e., where max_uncertainty == provided_uncertainty... we must solve
        #
        #   provided_uncertainty = least_num_strata // (resolution + 1)
        #
        # and
        #
        #   least_num_strata = num_strata_deposited - greatest_viable_rank

        # -1 due to *lack* of an in-progress deposition
        greatest_viable_rank = least_last_rank - provided_uncertainty * (
            resolution + 1
        )

        # calculate how many steps at provided_uncertainty interval we can take
        # +provided_uncertainty because greatest viable rank is the *last*
        # position we can take a step in our interval from
        num_interval_steps = (
            greatest_viable_rank + provided_uncertainty
        ) // provided_uncertainty
        cutoff_rank = num_interval_steps * provided_uncertainty

        if actual_rank_of_mrca < cutoff_rank:
            if actual_rank_of_mrca >= (
                least_last_rank - least_last_rank % provided_uncertainty
            ):
                return (least_last_rank - 1) % provided_uncertainty
            else:
                return provided_uncertainty - 1
        else:
            assert cutoff_rank
            return self(
                policy=policy,
                first_num_strata_deposited=least_num_strata_deposited
                - cutoff_rank,
                second_num_strata_deposited=least_num_strata_deposited
                - cutoff_rank,
                actual_rank_of_mrca=actual_rank_of_mrca - cutoff_rank,
            )
