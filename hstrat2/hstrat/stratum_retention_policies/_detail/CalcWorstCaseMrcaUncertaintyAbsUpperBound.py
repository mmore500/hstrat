import typing


class CalcWorstCaseMrcaUncertaintyAbsUpperBound:

    def __init__(
        self: 'CalcWorstCaseMrcaUncertaintyAbsUpperBound',
        policy_spec: typing.Optional[typing.Any]=None,
    ) -> None:
        pass

    def __eq__(
        self: 'CalcWorstCaseMrcaUncertaintyAbsUpperBound',
        other: typing.Any,
    ) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: 'CalcWorstCaseMrcaUncertaintyAbsUpperBound',
        policy: typing.Optional['Policy'],
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
        actual_rank_of_mrca: typing.Optional[int]=None,
    ) -> int:
        """At most, how much absolute uncertainty to estimate rank of MRCA?
        Inclusive."""

        return max(
            first_num_strata_deposited,
            second_num_strata_deposited,
        )
