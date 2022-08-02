import typing

from ..HereditaryStratum import HereditaryStratum
from ..stratum_retention_predicates \
    import StratumRetentionPredicateTaperedDepthProportionalResolution


class StratumRetentionCondemnerTaperedDepthProportionalResolution(
    # inherit CalcNumStrataRetainedUpperBound, etc.
    StratumRetentionPredicateTaperedDepthProportionalResolution,
):
    """Functor to implement the tapered depth-proportional resolution strata
    retention policy, for use with HereditaryStratigraphicColumn.

    This functor enacts the tapered depth-proportional resolution policy by
    specifying the set of strata ranks that should be purged from a hereditary
    stratigraphic column when the nth stratum is deposited.

    The tapered depth-proportional resolution policy ensures estimates of MRCA
    rank will have uncertainty bounds less than or equal to a user-specified
    proportion of the largest number of strata deposited on either column.
    Thus, MRCA rank estimate uncertainty scales as O(n) with respect to the
    greater number of strata deposited on either column.

    Under the tapered depth-proportional resolution policy, the number of strata
    retained (i.e., space complexity) scales as O(1) with respect to the number
    of strata deposited.

    See Also
    --------
    StratumRetentionPredicateTaperedDepthProportionalResolution:
        For definitions of methods inherited by this class that describe
        guaranteed properties of the depth resolution stratum retention
        policy.
    StratumRetentionCondemnerDepthProportionalResolution:
        For a predicate retention policy that achieves the same guarantees for
        depth-proportional resolution but purges unnecessary strata more
        aggressively and abruptly.
    """

    def __init__(
        self: 'StratumRetentionCondemnerTaperedDepthProportionalResolution',
        guaranteed_depth_proportional_resolution: int=10,
    ):
        """Construct the functor.

        Parameters
        ----------
        guaranteed_depth_proportional_resolution : int, optional
            The desired minimum number of intervals for the rank of the MRCA to
            be able to be distinguished between. The uncertainty of MRCA
            rank estimates provided under the depth-proportional resolution
            policy will scale as total number of strata deposited divided by
            guaranteed_depth_proportional_resolution.
        """

        super(
            StratumRetentionCondemnerTaperedDepthProportionalResolution,
            self,
        ).__init__(
            guaranteed_depth_proportional_resolution
                =guaranteed_depth_proportional_resolution,
        )

    def __call__(
        self: 'StratumRetentionCondemnerTaperedDepthProportionalResolution',
        num_stratum_depositions_completed: int,
        retained_ranks: typing.Optional[typing.Iterable[int]]=None,
    ) -> typing.Iterator[int]:
        """Decide which strata within the stratagraphic column should be purged.

        Every time a new stratum is deposited, this method is called to
        determine which strata should be purged. All strata at ranks yielded
        from this functor are immediately purged from the column, meaning that
        for a stratum to persist it must not be yielded by this functor each
        and every time a new stratum is deposited.

        Parameters
        ----------
        num_stratum_depositions_completed : int
            The number of strata that have already been deposited, not
            including the latest stratum being deposited which prompted the
            current purge operation.
        retained_ranks : iterator over int, optional
            An iterator over ranks of strata currently retained within the
            hereditary stratigraphic column. Not used in this functor.

        Returns
        -------
        iterator over int
            The ranks of strata that should be purged from the hereditary
            stratigraphic column at this deposition step.

        See Also
        --------
        StratumRetentionPredicateDepthProportionalResolution:
            For details on the rationale, implementation, and guarantees of the
            tapered depth-proportional resolution stratum retention policy.
        """

        resolution = self._guaranteed_depth_proportional_resolution
        # _guaranteed_depth_proportional_resolution is from super class

        # until sufficient strata have been deposited to reach target resolution
        # don't remove any strata
        if num_stratum_depositions_completed < 2 * resolution: return


        # +1's because of in-progress deposition
        # _calc_provided_uncertainty is from super class
        cur_stage_uncertainty = self._calc_provided_uncertainty(
            num_stratum_depositions_completed + 1
        )
        prev_stage_uncertainty = cur_stage_uncertainty // 2
        assert prev_stage_uncertainty

        cur_stage_idx \
            = num_stratum_depositions_completed // cur_stage_uncertainty
        prev_stage_idx \
            = num_stratum_depositions_completed // prev_stage_uncertainty

        # we just added a new peg so we have to clear out an old one
        if (num_stratum_depositions_completed % prev_stage_uncertainty == 0):

            target_idx = prev_stage_idx * 2 - 4 * resolution + 1
            target_rank = target_idx * prev_stage_uncertainty
            # assert target_rank <= num_stratum_depositions_completed
            assert target_rank >= 0
            if target_rank < num_stratum_depositions_completed:
                yield target_rank

        # newest stratum is in-progress deposition
        # that will occupy rank num_stratum_depositions_completed
        second_newest_stratum_rank = num_stratum_depositions_completed - 1
        # we always keep the newest stratum
        # but unless the now-second-newest stratum is needed as a waypoint
        # of the cur_provided_uncertainty intervals, we will get rid of it
        if (
            second_newest_stratum_rank % prev_stage_uncertainty
            or prev_stage_idx == 4 * resolution - 1
        ):
            # we always keep the newest stratum
            # but unless the now-second-newest stratum is needed as a waypoint
            # of the cur_provided_uncertainty intervals, get rid of it
            yield second_newest_stratum_rank
