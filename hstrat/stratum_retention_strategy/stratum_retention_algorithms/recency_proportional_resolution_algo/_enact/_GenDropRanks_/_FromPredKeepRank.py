import typing

from ...._detail import PolicyCouplerBase
from ...._impl import GenDropRanksFromPredKeepRank
from ..._PolicySpec import PolicySpec
from ..._impl import calc_provided_uncertainty


class _PredKeepRank:
    """Functor to implement the recency-proportional resolution stratum
    retention policy, for use with HereditaryStratigraphicColumn.

    This functor enacts the recency-proportional resolution policy by
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

    # TODO refactor to not be recursive?
    @staticmethod
    def _do_call(
        policy: PolicyCouplerBase,
        num_stratum_depositions_completed: int,
        stratum_rank: int,
    ) -> bool:
        """Implementation for __call__ to faciliate external (but within-
        library) calls."""
        resolution = policy.GetSpec().GetRecencyProportionalResolution()

        # to satisfy requirements of HereditaryStratigraphicColumn impl
        # we must always keep root ancestor and newest stratum
        if stratum_rank in (0, num_stratum_depositions_completed):
            return True
        elif num_stratum_depositions_completed <= resolution:
            return True

        provided_uncertainty = calc_provided_uncertainty(
            resolution,
            num_stratum_depositions_completed,
        )
        # see CalcRankAtColumnIndex
        greatest_viable_rank = (
            num_stratum_depositions_completed
            - provided_uncertainty * (resolution + 1)
        )
        # see CalcRankAtColumnIndex
        num_interval_steps = (
            greatest_viable_rank + provided_uncertainty
        ) // provided_uncertainty
        cutoff_rank = num_interval_steps * provided_uncertainty

        # logically,  we could just test
        #   if stratum_rank == provided_uncertainty: return True
        # but we are guaranteed to eventually return True under the weaker
        # condition
        #   if stratum_rank % provided_uncertainty == 0
        # so as an optimization go ahead and return True now if it holds
        if stratum_rank % provided_uncertainty == 0:
            return True
        elif stratum_rank <= cutoff_rank:
            return False
        else:
            assert cutoff_rank
            return _PredKeepRank._do_call(
                policy,
                num_stratum_depositions_completed - cutoff_rank,
                stratum_rank - cutoff_rank,
            )

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
        recency_proportional_resolution_algo:
            For details on the rationale, implementation, and guarantees of the
            recency-proportional resolution stratum retention policy.
        """
        return _PredKeepRank._do_call(
            policy,
            num_stratum_depositions_completed,
            stratum_rank,
        )


FromPredKeepRank = GenDropRanksFromPredKeepRank(_PredKeepRank)
