import typing

from ..HereditaryStratum import HereditaryStratum
from ..stratum_retention_predicates \
    import StratumRetentionPredicateRecencyProportionalResolution


class StratumRetentionCondemnerRecencyProportionalResolution(
    # inherit CalcNumStrataRetainedUpperBound, etc.
    StratumRetentionPredicateRecencyProportionalResolution,
):

    def __init__(
        self: 'StratumRetentionCondemnerRecencyProportionalResolution',
        guaranteed_mrca_recency_proportional_resolution: int=10,
    ):
        super(
            StratumRetentionCondemnerRecencyProportionalResolution,
            self,
        ).__init__(
            guaranteed_mrca_recency_proportional_resolution
                =guaranteed_mrca_recency_proportional_resolution,
        )

    def _num_to_condemn(
        self: 'StratumRetentionCondemnerRecencyProportionalResolution',
        num_stratum_depositions_completed: int,
    ) -> int:
        # how many strata should be eliminated after
        # num_stratum_depositions_completed have been deposited and the
        # num_stratum_depositions_completed + 1'th deposition is in progress?
        # This expression was extrapolated from
        # resolution = 0, https://oeis.org/A001511
        # resolution = 1, https://oeis.org/A091090
        # and is unit tested extensively.
        resolution = self._guaranteed_mrca_recency_proportional_resolution
        # _guaranteed_mrca_recency_proportional_resolution is from super class

        if num_stratum_depositions_completed % 2 == 1:
            return 0
        elif num_stratum_depositions_completed < 2 * (resolution + 1):
            return 0
        else:
            return \
                1 + self._num_to_condemn(num_stratum_depositions_completed // 2)

    def __call__(
        self: 'StratumRetentionCondemnerRecencyProportionalResolution',
        num_stratum_depositions_completed: int,
        retained_ranks: typing.Optional[typing.Iterable[int]]=None,
    ) -> typing.Iterator[int]:
        num_to_condemn = self._num_to_condemn(num_stratum_depositions_completed)
        resolution = self._guaranteed_mrca_recency_proportional_resolution
        # _guaranteed_mrca_recency_proportional_resolution is from super class

        for i in range(num_to_condemn):
            factor = 2 * resolution + 1
            num_ranks_back = factor * (2 ** i)
            yield num_stratum_depositions_completed - num_ranks_back
