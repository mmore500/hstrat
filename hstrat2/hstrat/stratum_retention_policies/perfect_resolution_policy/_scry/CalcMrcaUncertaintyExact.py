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
        return isinstance(other, CalcMrcaUncertaintyExact)

    def __call__(
        self: 'CalcMrcaUncertaintyExact',
        policy: typing.Optional['Policy'],
        first_num_strata_deposited: typing.Optional[int],
        second_num_strata_deposited: typing.Optional[int],
        actual_rank_of_mrca: typing.Optional[int],
    ) -> int:
        """Exactly how much uncertainty to estimate rank of MRCA?"""

        return 0
