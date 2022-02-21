import typing

from ..HereditaryStratum import HereditaryStratum
from ..stratum_retention_predicates \
    import StratumRetentionPredicatePerfectResolution


class StratumRetentionCondemnerPerfectResolution(
    # inherit CalcNumStrataRetainedUpperBound, etc.
    StratumRetentionPredicatePerfectResolution,
):

    def __call__(
        self: 'StratumRetentionCondemnerPerfectResolution',
        retained_ranks: typing.Optional[typing.Iterable[int]]=None,
        num_strata_deposited: typing.Optional[int]=None,
    ) -> typing.Iterator[int]:
        # empty generator
        # see https://stackoverflow.com/a/13243870/17332200
        return
        yield
