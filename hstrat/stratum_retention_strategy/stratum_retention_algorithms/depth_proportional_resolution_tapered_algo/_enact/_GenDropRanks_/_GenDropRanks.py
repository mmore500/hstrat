import typing

from ...._detail import PolicyCouplerBase
from ..._PolicySpec import PolicySpec
from ..._impl import calc_provided_uncertainty


class GenDropRanks:
    """Functor to implement the tapered depth-proportional resolution stratum
    retention policy, for use with HereditaryStratigraphicColumn.

    This functor enacts the tapered depth-proportional resolution policy by
    specifying the set of strata ranks that should be purged from a hereditary
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
        depth_proportional_resolution_tapered_algo:
            For details on the rationale, implementation, and guarantees of the
            tapered depth-proportional resolution stratum retention policy.
        """
        spec = policy.GetSpec()
        resolution = spec.GetDepthProportionalResolution()

        # until sufficient strata have been deposited to reach target resolution
        # don't remove any strata
        if num_stratum_depositions_completed < 2 * resolution + 1:
            return

        cur_stage_uncertainty = calc_provided_uncertainty(
            resolution, num_stratum_depositions_completed
        )
        prev_stage_uncertainty = cur_stage_uncertainty // 2
        assert prev_stage_uncertainty

        prev_stage_idx = (
            num_stratum_depositions_completed - 1
        ) // prev_stage_uncertainty

        second_newest_stratum_rank = num_stratum_depositions_completed - 1
        # we just added a new peg so we have to clear out an old one
        if second_newest_stratum_rank % prev_stage_uncertainty == 0:

            target_idx = prev_stage_idx * 2 - 4 * resolution + 1
            target_rank = target_idx * prev_stage_uncertainty
            if 0 < target_rank < num_stratum_depositions_completed:
                yield target_rank

        else:
            # newest stratum is in-progress deposition
            # that will occupy rank num_stratum_depositions_completed
            # we always keep the newest stratum
            # but because we know the second newest is not needed as a waypoint
            # we will get rid of it
            yield second_newest_stratum_rank
