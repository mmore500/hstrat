import math
import typing

from ..._detail import CalcWorstCaseMrcaUncertaintyRelUpperBound

from .._impl import calc_common_ratio
from ..PolicySpec import PolicySpec


class CalcMrcaUncertaintyRelUpperBound:
    """Functor to provide member function implementation in Policy class."""

    def __init__(
        self: 'CalcMrcaUncertaintyRelUpperBound',
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        pass

    def __eq__(
        self: 'CalcMrcaUncertaintyRelUpperBound',
        other: typing.Any,
    ) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: 'CalcMrcaUncertaintyRelUpperBound',
        policy: 'Policy',
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
        actual_rank_of_mrca: typing.Optional[int],
    ) -> float:
        """At most, how much relative uncertainty to estimate rank of MRCA?
        Inclusive."""

        spec = policy.GetSpec()

        interspersal = spec._interspersal
        # edge case: no uncertainty guarantee for interspersal 1
        # interspersal >= 2 required for uncertainty guarantee
        if interspersal == 1:
            return CalcWorstCaseMrcaUncertaintyRelUpperBound()(
                policy,
                first_num_strata_deposited,
                second_num_strata_deposited,
                actual_rank_of_mrca,
            )

        if 0 in (first_num_strata_deposited, second_num_strata_deposited):
            return 0.0

        min_num_strata_deposited, max_num_strata_deposited = sorted([
            first_num_strata_deposited,
            second_num_strata_deposited,
        ])

        length_ratio = max_num_strata_deposited / min_num_strata_deposited

        common_ratio = calc_common_ratio(spec._degree, max_num_strata_deposited)

        return length_ratio * common_ratio / (interspersal - 1)
