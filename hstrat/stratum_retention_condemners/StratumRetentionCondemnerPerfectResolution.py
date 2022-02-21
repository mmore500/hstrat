import typing

from ..HereditaryStratum import HereditaryStratum


class StratumRetentionCondemnerPerfectResolution:

    def __call__(
        self: 'StratumRetentionCondemnerPerfectResolution',
        retained_ranks: typing.Optional[typing.Iterable[int]]=None,
        num_strata_deposited: typing.Optional[int]=None,
    ) -> typing.Iterator[int]:
        # empty generator
        # see https://stackoverflow.com/a/13243870/17332200
        return
        yield

    def __eq__(
        self: 'StratumRetentionCondemnerPerfectResolution',
        other: 'StratumRetentionCondemnerPerfectResolution',
    ) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def CalcNumStrataRetainedUpperBound(
        self: 'StratumRetentionCondemnerPerfectResolution',
        num_strata_deposited: int,
    ) -> int:
        return num_strata_deposited

    def CalcMrcaUncertaintyUpperBound(
        self: 'StratumRetentionCondemnerPerfectResolution',
        *,
        first_num_strata_deposited: typing.Optional[int]=None,
        second_num_strata_deposited: typing.Optional[int]=None,
        actual_rank_of_mrca: typing.Optional[int]=None,
    ) -> int:
        return 0

    def CalcRankAtColumnIndex(
        self: 'StratumRetentionCondemnerPerfectResolution',
        index: int,
        num_strata_deposited: typing.Optional[int]=None,
    ) -> int:
        return index
