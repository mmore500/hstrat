import typing


class StratumRetentionPredicateNominalResolution:

    def __call__(
        self: 'StratumRetentionPredicateNominalResolution',
        stratum_rank: int,
        column_strata_deposited: int,
    ) -> bool:
        return stratum_rank in (0, column_strata_deposited)

    def __eq__(
        self: 'StratumRetentionPredicateNominalResolution',
        other: 'StratumRetentionPredicateNominalResolution',
    ) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def CalcNumStrataRetainedUpperBound(
        self: 'StratumRetentionPredicateNominalResolution',
        num_strata_deposited: typing.Optional[int]=None,
    ) -> int:
        return 2

    def CalcMrcaUncertaintyUpperBound(
        self: 'StratumRetentionPredicateNominalResolution',
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
        self: 'StratumRetentionPredicateNominalResolution',
        index: int,
        num_strata_deposited: int,
    ) -> int:
        return [
            0,
            num_strata_deposited - 1,
            num_strata_deposited,
        ][index]
