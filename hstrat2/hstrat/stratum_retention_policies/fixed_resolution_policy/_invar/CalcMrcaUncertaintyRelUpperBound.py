import typing

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
        actual_rank_of_mrca: int,
    ) -> float:
        """At most, how much relative uncertainty to estimate rank of MRCA? Inclusive."""

        spec = policy.GetSpec()

        abs_upper_bound = policy.CalcMrcaUncertaintyAbsUpperBound(
            first_num_strata_deposited,
            second_num_strata_deposited,
            actual_rank_of_mrca,
        )

        # worst-case recency is 1
        return abs_upper_bound / 1.0
