import typing

from ..HereditaryStratum import HereditaryStratum

class StratumRetentionFilterMaximal:

    def __call__(
        self: 'StratumRetentionFilterMaximal',
        strat_col: 'HereditaryStratigraphicColumn',
    ) -> typing.List[HereditaryStratum]:
        return strat_col._column

    def __eq__(
        self: 'StratumRetentionFilterMaximal',
        other: 'StratumRetentionFilterMaximal',
    ) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def CalcNumStrataRetainedUpperBound(
        self: 'StratumRetentionFilterMaximal',
        num_strata_deposited: int,
    ) -> int:
        return num_strata_deposited

    def CalcMrcaUncertaintyUpperBound(
        self: 'StratumRetentionFilterMaximal',
        *,
        first_num_strata_deposited: typing.Optional[int]=None,
        second_num_strata_deposited: typing.Optional[int]=None,
        actual_rank_of_mrca: typing.Optional[int]=None,
    ) -> int:
        return 0

    def CalcRankAtColumnIndex(
        self: 'StratumRetentionFilterMaximal',
        index: int,
        num_strata_deposited: typing.Optional[int]=None,
    ) -> int:
        return index
