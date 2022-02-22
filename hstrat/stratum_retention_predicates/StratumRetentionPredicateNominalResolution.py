import typing


class StratumRetentionPredicateNominalResolution:

    def __call__(
        self: 'StratumRetentionPredicateNominalResolution',
        stratum_rank: int,
        num_stratum_depositions_completed: int,
    ) -> bool:
        return stratum_rank in (0, num_stratum_depositions_completed)

    def __eq__(
        self: 'StratumRetentionPredicateNominalResolution',
        other: 'StratumRetentionPredicateNominalResolution',
    ) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def CalcNumStrataRetainedExact(
        self: 'StratumRetentionPredicateNominalResolution',
        num_strata_deposited: int,
    ) -> int:
        return min(num_strata_deposited, 2)

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
