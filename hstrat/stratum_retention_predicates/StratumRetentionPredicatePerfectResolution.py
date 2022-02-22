import typing


class StratumRetentionPredicatePerfectResolution:

    def __call__(
        self: 'StratumRetentionPredicatePerfectResolution',
        stratum_rank: typing.Optional[int]=None,
        num_stratum_depositions_completed: typing.Optional[int]=None,
    ) -> bool:
        return True

    def __eq__(
        self: 'StratumRetentionPredicatePerfectResolution',
        other: 'StratumRetentionPredicatePerfectResolution',
    ) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def CalcNumStrataRetainedExact(
        self: 'StratumRetentionPredicatePerfectResolution',
        num_strata_deposited: int,
    ) -> int:
        return num_strata_deposited

    def CalcNumStrataRetainedUpperBound(
        self: 'StratumRetentionPredicatePerfectResolution',
        num_strata_deposited: int,
    ) -> int:
        return self.CalcNumStrataRetainedExact(
            num_strata_deposited=num_strata_deposited,
        )

    def CalcMrcaUncertaintyUpperBound(
        self: 'StratumRetentionPredicatePerfectResolution',
        *,
        first_num_strata_deposited: typing.Optional[int]=None,
        second_num_strata_deposited: typing.Optional[int]=None,
        actual_rank_of_mrca: typing.Optional[int]=None,
    ) -> int:
        return 0

    def CalcRankAtColumnIndex(
        self: 'StratumRetentionPredicatePerfectResolution',
        index: int,
        num_strata_deposited: typing.Optional[int]=None,
    ) -> int:
        return index
