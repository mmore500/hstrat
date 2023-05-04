import typing

from ...._detail import PolicyCouplerBase
from ...._impl import GenDropRanksFromPredKeepRank
from ..._PolicySpec import PolicySpec
from ..._impl import calc_provided_uncertainty


class _PredKeepRank:
    """Functor to implement the tapered depth-proportional resolution stratum
    retention policy, for use with HereditaryStratigraphicColumn.

    This functor enacts the tapered depth-proportional resolution policy by
    specifying the set of strata ranks that should be purged from a hereditary
    stratigraphic column when the nth stratum is deposited.
    """

    def __init__(
        self: "_PredKeepRank",
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        pass

    def __eq__(self: "_PredKeepRank", other: typing.Any) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "_PredKeepRank",
        policy: PolicyCouplerBase,
        num_stratum_depositions_completed: int,
        stratum_rank: int,
    ) -> bool:
        """Decide if a stratum within the stratagraphic column should be
        retained or purged.

        Every time a new stratum is deposited, this method is called on each
        stratum present in a HereditaryStratigraphicColumn to determine whether
        it should be retained. Strata that return False are immediately purged
        from the column, meaning that for a stratum to persist it must earn a
        True result from this method each and every time a new stratum is
        deposited.

        Parameters
        ----------
        policy: Policy
            Policy this functor enacts.
        stratum_rank : int
            The number of strata that were deposited before the stratum under
            consideration for retention.
        num_stratum_depositions_completed : int
            The number of strata that have already been deposited, not
            including the latest stratum being deposited which prompted the
            current purge operation.

        Returns
        -------
        bool
            True if the stratum should be retained, False otherwise.

        See Also
        --------
        depth_proportional_resolution_tapered_algo:
            For details on the rationale, implementation, and guarantees of the
            depth-proportional resolution stratum retention policy.
        """
        spec = policy.GetSpec()
        guaranteed_resolution = spec.GetDepthProportionalResolution()

        # easy edge cases we must always retain
        if (
            # always retain newest stratum
            stratum_rank == num_stratum_depositions_completed
            # retain all strata until more than num_intervals are deposited
            or num_stratum_depositions_completed < guaranteed_resolution
        ):
            return True

        # +1 because of in-progress deposition
        cur_stage_uncertainty = calc_provided_uncertainty(
            guaranteed_resolution,
            num_stratum_depositions_completed + 1,
        )

        # keep unused variables for comprehensibility
        cur_stage_idx = stratum_rank // cur_stage_uncertainty  # noqa: F841
        cur_stage_max_idx = (  # noqa: F841
            num_stratum_depositions_completed // cur_stage_uncertainty
        )

        # use lambdas to prevent division by zero
        prev_stage_uncertainty = cur_stage_uncertainty // 2

        def prev_stage_idx() -> int:
            return stratum_rank // prev_stage_uncertainty

        def prev_stage_max_idx() -> int:
            return (
                num_stratum_depositions_completed - 1
            ) // prev_stage_uncertainty

        return stratum_rank % cur_stage_uncertainty == 0 or (
            stratum_rank % prev_stage_uncertainty == 0
            and prev_stage_idx()
            > 2 * prev_stage_max_idx() - 4 * guaranteed_resolution + 1
        )


FromPredKeepRank = GenDropRanksFromPredKeepRank(_PredKeepRank)
