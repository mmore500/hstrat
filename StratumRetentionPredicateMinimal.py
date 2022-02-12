import typing


class StratumRetentionPredicateMinimal:

    def __call__(
        self: 'StratumRetentionPredicateMinimal',
        stratum_rank: int,
        column_strata_deposited: int,
    ) -> bool:
        return stratum_rank in (0, column_strata_deposited)

    def __eq__(
        self: 'StratumRetentionPredicateMinimal',
        other: 'StratumRetentionPredicateMinimal',
    ) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def CalcNumStrataRetainedUpperBound(
        self: 'StratumRetentionPredicateMinimal',
        num_strata_deposited: typing.Optional[int]=None,
    ) -> int:
        return 2

    def CalcMrcaUncertaintyUpperBound(
        self: 'StratumRetentionPredicateMinimal',
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

    def CalcRankAtColumnIndex(
        self: 'StratumRetentionPredicateMinimal',
        index: int,
        num_strata_deposited: int,
    ) -> int:
        return [
            0,
            num_strata_deposited - 1,
            num_strata_deposited,
        ][index]
