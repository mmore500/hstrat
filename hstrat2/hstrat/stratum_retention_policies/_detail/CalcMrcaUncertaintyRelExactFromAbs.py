import typing


class CalcMrcaUncertaintyRelExactFromAbs:

    def __init__(
        self: 'CalcMrcaUncertaintyRelExactFromAbs',
        policy_spec: typing.Optional[typing.Any]=None,
    ) -> None:
        pass

    def __eq__(
        self: 'CalcMrcaUncertaintyRelExactFromAbs',
        other: typing.Any,
    ) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: 'CalcMrcaUncertaintyRelExactFromAbs',
        policy: typing.Optional['Policy'],
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
        actual_rank_of_mrca: int,
    ) -> float:
        """At most, how much absolute uncertainty to estimate rank of MRCA?
        Inclusive."""

        if (
            first_num_strata_deposited <= 2
            or second_num_strata_deposited <= 2
            or actual_rank_of_mrca in (
                first_num_strata_deposited - 1,
                second_num_strata_deposited - 1,
            )
        ):
            return 0.0

        uncertainty_abs_exact = policy.CalcMrcaUncertaintyAbsExact(
            first_num_strata_deposited,
            second_num_strata_deposited,
            actual_rank_of_mrca,
        )

        least_last_rank = min(
            first_num_strata_deposited - 1,
            second_num_strata_deposited - 1,
        )
        least_recency = least_last_rank - actual_rank_of_mrca

        return uncertainty_abs_exact / least_recency
