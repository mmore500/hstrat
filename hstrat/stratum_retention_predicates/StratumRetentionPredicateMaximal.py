import typing


class StratumRetentionPredicateMaximal:

    def __call__(
        self: 'StratumRetentionPredicateMaximal',
        stratum_rank: int,
        column_strata_deposited: int,
    ) -> bool:
        return True

    def __eq__(
        self: 'StratumRetentionPredicateMaximal',
        other: 'StratumRetentionPredicateMaximal',
    ) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def CalcNumStrataRetainedUpperBound(
        self: 'StratumRetentionPredicateMaximal',
        num_strata_deposited: int,
    ) -> int:
        return num_strata_deposited

    def CalcMrcaUncertaintyUpperBound(
        self: 'StratumRetentionPredicateMaximal',
        *,
        first_num_strata_deposited: typing.Optional[int]=None,
        second_num_strata_deposited: typing.Optional[int]=None,
        actual_rank_of_mrca: typing.Optional[int]=None,
    ) -> int:
        return 0

    def CalcRankAtColumnIndex(
        self: 'StratumRetentionPredicateMaximal',
        index: int,
        num_strata_deposited: typing.Optional[int]=None,
    ) -> int:
        return index
