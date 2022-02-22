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
        num_stratum_depositions_completed: int,
        retained_ranks: typing.Optional[typing.Iterable[int]]=None,
    ) -> typing.Iterator[int]:
        # in-progress deposition not reflected in
        # num_stratum_depositions_completed
        if num_stratum_depositions_completed > 1:
            yield num_stratum_depositions_completed - 1
