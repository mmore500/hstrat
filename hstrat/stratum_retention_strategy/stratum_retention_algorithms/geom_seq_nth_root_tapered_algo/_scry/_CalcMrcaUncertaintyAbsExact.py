import operator
import typing

from ....._auxiliary_lib import find_bounds
from ..._detail import PolicyCouplerBase
from .._PolicySpec import PolicySpec
from .._impl import get_retained_ranks


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

        least_num_strata_deposited = min(
            first_num_strata_deposited,
            second_num_strata_deposited,
        )
        least_last_rank = least_num_strata_deposited - 1

        retained_ranks = get_retained_ranks(
            policy,
            least_num_strata_deposited,
        )
        lower_bound, upper_bound = find_bounds(
            query=actual_rank_of_mrca,
            iterable=retained_ranks,
            filter_below=operator.le,
            filter_above=operator.gt,
            initializer=(0, least_num_strata_deposited),
        )

        assert lower_bound < upper_bound
        return upper_bound - lower_bound - 1
