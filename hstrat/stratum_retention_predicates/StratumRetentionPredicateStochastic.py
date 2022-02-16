import random
import typing


class StratumRetentionPredicateStochastic:

    def __call__(
        self: 'StratumRetentionPredicateStochastic',
        stratum_rank: int,
        column_strata_deposited: int,
    ) -> bool:
        if stratum_rank and stratum_rank == column_strata_deposited - 2:
            return random.choice([True, False])
        else: return True

    def __eq__(
        self: 'StratumRetentionPredicateStochastic',
        other: 'StratumRetentionPredicateStochastic',
    ) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def CalcNumStrataRetainedUpperBound(
        self: 'StratumRetentionPredicateStochastic',
        num_strata_deposited: int,
    ) -> int:
        return num_strata_deposited

    def CalcMrcaUncertaintyUpperBound(
        self: 'StratumRetentionPredicateStochastic',
        *,
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
        actual_rank_of_mrca: typing.Optional[int]=None,
    ) -> int:
        # essentially, no guarantee given
        return max(
            first_num_strata_deposited,
            second_num_strata_deposited,
        )
