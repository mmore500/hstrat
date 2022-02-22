import typing

from ..HereditaryStratum import HereditaryStratum
from ..stratum_retention_predicates \
    import StratumRetentionPredicateDepthProportionalResolution


class StratumRetentionCondemnerDepthProportionalResolution(
    # inherit CalcNumStrataRetainedUpperBound, etc.
    StratumRetentionPredicateDepthProportionalResolution,
):

    def __init__(
        self: 'StratumRetentionCondemnerDepthProportionalResolution',
        guaranteed_depth_proportional_resolution: int=10,
    ):
        super(
            StratumRetentionCondemnerDepthProportionalResolution,
            self,
        ).__init__(
            guaranteed_depth_proportional_resolution
                =guaranteed_depth_proportional_resolution,
        )

    def __call__(
        self: 'StratumRetentionCondemnerDepthProportionalResolution',
        num_stratum_depositions_completed: int,
        retained_ranks: typing.Optional[typing.Iterable[int]]=None,
    ) -> typing.Iterator[int]:
        resolution = self._guaranteed_depth_proportional_resolution
        # _guaranteed_depth_proportional_resolution is from super class

        # until sufficient strata have been deposited to reach target resolution
        # don't remove any strata
        if num_stratum_depositions_completed <= resolution: return

        # newest stratum is in-progress deposition
        # that will occupy rank num_stratum_depositions_completed
        second_newest_stratum_rank = num_stratum_depositions_completed - 1
        # +1's because of in-progress deposition
        # _calc_provided_uncertainty is from super class
        cur_provided_uncertainty = self._calc_provided_uncertainty(
            num_stratum_depositions_completed + 1
        )
        prev_provided_uncertainty = self._calc_provided_uncertainty(
            num_stratum_depositions_completed + 1
            - 1
        )
        if cur_provided_uncertainty != prev_provided_uncertainty:
            # we just passed the threshold where the spacing between retained
            # strata could be doubled without violating our resolution guarantee
            # clean up no-longer-needed strata that bisect
            # cur_provided_uncertainty intervals
            assert prev_provided_uncertainty * 2 == cur_provided_uncertainty
            yield from range(
                prev_provided_uncertainty,
                second_newest_stratum_rank,
                cur_provided_uncertainty,
            )

        if second_newest_stratum_rank % cur_provided_uncertainty:
            # we always keep the newest stratum
            # but unless the now-second-newest stratum is needed as a waypoint
            # of the cur_provided_uncertainty intervals, get rid of it
            yield second_newest_stratum_rank
