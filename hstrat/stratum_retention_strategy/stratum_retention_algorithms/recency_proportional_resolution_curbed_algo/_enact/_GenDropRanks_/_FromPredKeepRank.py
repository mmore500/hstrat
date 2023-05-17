import typing

from ...._detail import PolicyCouplerBase
from ...._impl import GenDropRanksFromPredKeepRank
from ....geom_seq_nth_root_algo._enact._GenDropRanks_._FromPredKeepRank import (
    _PredKeepRank as gsnra_PredKeepRank,
)
from ....recency_proportional_resolution_algo._enact._GenDropRanks_._FromPredKeepRank import (
    _PredKeepRank as rpra_PredKeepRank,
)
from ..._PolicySpec import PolicySpec
from ..._impl import pick_policy


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
        dispatched_policy = pick_policy(
            policy.GetSpec().GetSizeCurb(),
            num_stratum_depositions_completed + 1,
        )
        return {
            "recency_proportional_resolution_algo": rpra_PredKeepRank,
            "geom_seq_nth_root_algo": gsnra_PredKeepRank,
        }[dispatched_policy.GetSpec().GetAlgoIdentifier()]._do_call(
            dispatched_policy, num_stratum_depositions_completed, stratum_rank
        )


FromPredKeepRank = GenDropRanksFromPredKeepRank(_PredKeepRank)
