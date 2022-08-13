import typing

from ..._detail import CalcWorstCaseMrcaUncertaintyRelUpperBound

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
        """At most, how much uncertainty to estimate rank of MRCA? Inclusive."""

        spec = policy.GetSpec()

        if 0 in (first_num_strata_deposited, second_num_strata_deposited):
            return 0.0

        min_num_strata_deposited, max_num_strata_deposited = sorted([
            first_num_strata_deposited,
            second_num_strata_deposited,
        ])

        length_ratio = max_num_strata_deposited / min_num_strata_deposited

        max_ranks_since_mrca = max(
            first_num_strata_deposited,
            second_num_strata_deposited,
        ) - actual_rank_of_mrca


        if spec._guaranteed_mrca_recency_proportional_resolution == 0:
            return CalcWorstCaseMrcaUncertaintyRelUpperBound()(
                policy,
                first_num_strata_deposited,
                second_num_strata_deposited,
                actual_rank_of_mrca,
            )
        else: return (
            length_ratio
            / spec._guaranteed_mrca_recency_proportional_resolution
        )
