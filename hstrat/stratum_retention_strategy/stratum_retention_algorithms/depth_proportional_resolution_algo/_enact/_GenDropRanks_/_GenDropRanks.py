import typing

from ...._detail import PolicyCouplerBase
from ..._PolicySpec import PolicySpec
from ..._impl import calc_provided_uncertainty


class GenDropRanks:
    """Functor to implement the depth-proportional resolution stratum retention
    policy, for use with HereditaryStratigraphicColumn.

    This functor enacts the depth-proportional resolution policy by specifying
    the set of strata ranks that should be purged from a hereditary
    stratigraphic column when the nth stratum is deposited.
    """

    def __init__(
        self: "GenDropRanks",
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        pass

    def __eq__(self: "GenDropRanks", other: typing.Any) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "GenDropRanks",
        policy: PolicyCouplerBase,
        num_stratum_depositions_completed: int,
        retained_ranks: typing.Optional[typing.Iterable[int]],
    ) -> typing.Iterator[int]:
        """Decide which strata within the stratagraphic column should be purged.

        Every time a new stratum is deposited, this method is called to
        determine which strata should be purged. All strata at ranks yielded
        from this functor are immediately purged from the column, meaning that
        for a stratum to persist it must not be yielded by this functor each
        and every time a new stratum is deposited.

        Parameters
        ----------
        policy: Policy
            Policy this functor enacts.
        num_stratum_depositions_completed : int
            The number of strata that have already been deposited, not
            including the latest stratum being deposited which prompted the
            current purge operation.
        retained_ranks : iterator over int
            An iterator over ranks of strata currently retained within the
            hereditary stratigraphic column. Not used in this functor.

        Returns
        -------
        iterator over int
                The ranks of strata that should be purged from the hereditary
            stratigraphic column at this deposition step.

        See Also
        --------
        depth_proportional_resolution_algo:
            For details on the rationale, implementation, and guarantees of the
            depth-proportional resolution stratum retention policy.
        """
        spec = policy.GetSpec()
        resolution = spec.GetDepthProportionalResolution()

        # until sufficient strata have been deposited to reach target resolution
        # don't remove any strata
        if num_stratum_depositions_completed <= resolution:
            return

        # newest stratum is in-progress deposition
        # that will occupy rank num_stratum_depositions_completed
        second_newest_stratum_rank = num_stratum_depositions_completed - 1
        # +1's because of in-progress deposition
        # _calc_provided_uncertainty is from super class
        cur_provided_uncertainty = calc_provided_uncertainty(
            resolution,
            num_stratum_depositions_completed + 1,
        )
        prev_provided_uncertainty = calc_provided_uncertainty(
            resolution,
            num_stratum_depositions_completed + 1 - 1,
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
