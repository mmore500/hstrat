import typing

from ..HereditaryStratum import HereditaryStratum
from ..stratum_retention_predicates \
    import StratumRetentionPredicateNominalResolution


class StratumRetentionCondemnerNominalResolution(
    # inherit CalcNumStrataRetainedUpperBound, etc.
    StratumRetentionPredicateNominalResolution,
):

    def __call__(
        self: 'StratumRetentionCondemnerNominalResolution',
        num_strata_deposited: int,
        retained_ranks: typing.Optional[typing.Iterable[int]]=None,
    ) -> typing.Iterator[int]:
        # in-progress deposition not reflected in num_strata_deposited
        if num_strata_deposited > 1:
            yield num_strata_deposited - 1
