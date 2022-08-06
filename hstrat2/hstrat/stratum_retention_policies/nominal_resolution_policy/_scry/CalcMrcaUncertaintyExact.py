import typing

from ..PolicySpec import PolicySpec

class CalcMrcaUncertaintyExact:
    """Functor to provide member function implementation in Policy class."""

    def __init__(
        self: 'CalcMrcaUncertaintyExact',
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        pass

    def __eq__(
        self: 'CalcMrcaUncertaintyExact',
        other: typing.Any,
    ) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: 'CalcMrcaUncertaintyExact',
        policy: typing.Optional['Policy'],
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
        actual_rank_of_mrca: int,
    ) -> int:
        """Exactly how much uncertainty to estimate rank of MRCA?"""

        least_num_strata_deposited = min(
            first_num_strata_deposited,
            second_num_strata_deposited,
        )
        if actual_rank_of_mrca == least_num_strata_deposited - 1:
            return 0
        else:
            return max(least_num_strata_deposited - 2, 0)
