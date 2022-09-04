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
        resolution = spec.GetRecencyProportionalResolution()

        # calculate the interval between retained strata we're starting out with
        # -1 due to *lack* of an in-progress deposition
        provided_uncertainty = calc_provided_uncertainty(
            resolution,
            num_strata_deposited - 1,
        )
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
        greatest_viable_rank = (
            num_strata_deposited - 1 - provided_uncertainty * (resolution + 1)
        )

        # calculate how many steps at provided_uncertainty interval we can take
        # +provided_uncertainty because greatest viable rank is the *last*
        # position we can take a step in our interval from
        num_interval_steps = (
            greatest_viable_rank + provided_uncertainty
        ) // provided_uncertainty

        if index <= num_interval_steps or provided_uncertainty == 1:
            # we can reach index within the current provided_uncertainty stage
            # note: must always enter base case when provided uncertainty is 1
            # or infinite recursion will result
            return index * provided_uncertainty
        else:
            # take as many index steps as possible at current uncertainty stage
            # and add number of ranks accrued at subsequent uncertainty stages
            num_ranks_traversed = num_interval_steps * provided_uncertainty
            return num_ranks_traversed + self(
                policy=policy,
                index=index - num_interval_steps,
                num_strata_deposited=num_strata_deposited
                - num_ranks_traversed,
            )
