import typing

from ..PolicySpec import PolicySpec

class CalcMrcaUncertaintyUpperBound:
    """Functor to provide member function implementation in Policy class."""

    def __init__(
        self: 'CalcMrcaUncertaintyUpperBound',
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        pass

    def __eq__(
        self: 'CalcMrcaUncertaintyUpperBound',
        other: typing.Any,
    ) -> bool:
        return isinstance(other, CalcMrcaUncertaintyUpperBound)

    def __call__(
        self: 'CalcMrcaUncertaintyUpperBound',
        policy: typing.Optional['Policy'],
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
        actual_rank_of_mrca: typing.Optional[int],
    ) -> int:
        """At most, how much uncertainty to estimate rank of MRCA? Inclusive."""

        spec = policy.GetSpec()

        return spec._fixed_resolution - 1
