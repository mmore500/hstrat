import opytional as opyt
import typing

from .CalcWorstCaseMrcaUncertaintyAbsUpperBound \
    import CalcWorstCaseMrcaUncertaintyAbsUpperBound

class CalcWorstCaseMrcaUncertaintyRelUpperBound:

    def __init__(
        self: 'CalcWorstCaseMrcaUncertaintyRelUpperBound',
        policy_spec: typing.Optional[typing.Any]=None,
    ) -> None:
        pass

    def __eq__(
        self: 'CalcWorstCaseMrcaUncertaintyRelUpperBound',
        other: typing.Any,
    ) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: 'CalcWorstCaseMrcaUncertaintyRelUpperBound',
        policy: typing.Optional['Policy'],
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
        actual_rank_of_mrca: int,
    ) -> float:
        """At most, how much uncertainty to relative estimate rank of MRCA?
        Inclusive."""

        if 0 in (first_num_strata_deposited, second_num_strata_deposited):
            return 0.0

        least_last_rank = min(
            first_num_strata_deposited - 1,
            second_num_strata_deposited - 1,
        )

        # conservatively normalize by smallest ranks since mrca
        min_ranks_since_mrca = least_last_rank - actual_rank_of_mrca
        worst_abs_uncertainty = CalcWorstCaseMrcaUncertaintyAbsUpperBound()(
            policy,
            first_num_strata_deposited,
            second_num_strata_deposited,
            actual_rank_of_mrca,
        )

        if min_ranks_since_mrca == 0:
            return 0.0
        else:
            return worst_abs_uncertainty / min_ranks_since_mrca
