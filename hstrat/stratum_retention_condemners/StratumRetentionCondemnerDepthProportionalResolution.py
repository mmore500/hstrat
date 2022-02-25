import typing

from ..HereditaryStratum import HereditaryStratum
from ..stratum_retention_predicates \
    import StratumRetentionPredicateDepthProportionalResolution


class StratumRetentionCondemnerDepthProportionalResolution(
    # inherit CalcNumStrataRetainedUpperBound, etc.
    StratumRetentionPredicateDepthProportionalResolution,
):
    """Functor to implement the depth-proportional resolution strata retention
    policy, for use with HereditaryStratigraphicColumn.

    This functor enacts the depth-proportional resolution policy by specifying
    the set of strata ranks that should be purged from a hereditary
    stratigraphic column when the nth stratum is deposited.

    The depth-proportional resolution policy ensures estimates of MRCA rank will
    have uncertainty bounds less than or equal to a user-specified
    proportion of the largest number of strata deposited on either column.
    Thus, MRCA rank estimate uncertainty scales as O(n) with respect to the
    greater number of strata deposited on either column.

    Under the depth-proportional resolution policy, the number of strata
    retained (i.e., space complexity) scales as O(1) with respect to the number
    of strata deposited.

    See Also
    --------
    StratumRetentionPredicateDepthProportionalResolution:
        For definitions of methods inherited by this class that describe
        guaranteed properties of the depth resolution stratum retention
        policy.
    """

    def __init__(
        self: 'StratumRetentionCondemnerDepthProportionalResolution',
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
            depth-proportional resolution stratum retention policy.
        """

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
