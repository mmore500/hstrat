import random
import typing


class StratumRetentionPredicateStochastic:
    """Functor to implement the stochastic resolution strata retention policy, for
    use with HereditaryStratigraphicColumn.

    This functor enacts the stochastic resolution policy by specifying
    whether a stratum with deposition rank r should be retained within the
    hereditary stratigraphic column after n strata have been deposited.

    The stochastic resolution policy retains strata probabilistically. It would
    be a poor choice to use in practice because mismatches between the
    particular ranks that each column happens to have strata for will degrade
    the effectiveness of comparisons between columns. Rather, it is included in
    the library as an edge case for testing purposes. Worst-case MRCA rank estimate uncertainty scales as O(n) with respect to the greater number of strata deposited on either column being compared.

    Under the stochastic resolution policy, the worst and average case number
    of strata retained (i.e., space complexity) scales as O(n) with respect to
    the number of strata deposited.
    """

    def __call__(
        self: 'StratumRetentionPredicateStochastic',
        stratum_rank: int,
        num_stratum_depositions_completed: int,
    ) -> bool:
        """Decide if a stratum within the stratagraphic column should be
        retained or purged.

        Every time a new stratum is deposited, this method is called on each
        stratum present in a HereditaryStratigraphicColumn to determine whether
        it should be retained. Strata that return False are immediately purged
        from the column, meaning that for a stratum to persist it must earn a
        True result from this method each and every time a new stratum is
        deposited.

        This functor's retention policy implementation guarantees that the most
        ancient and most recent strata will always be retained. For the
        secondmost recently deposited sratum, a pseudorandom coin flip is
        performed. Depending on the outcome of that coin flip, the stratum is either immediately purged or retained permanently.

        Parameters
        ----------
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
        """

        if (
            stratum_rank
            and stratum_rank == num_stratum_depositions_completed - 2
        ):
            return random.choice([True, False])
        else: return True

    def __eq__(
        self: 'StratumRetentionPredicateStochastic',
        other: 'StratumRetentionPredicateStochastic',
    ) -> bool:
        """Compare for value-wise equality."""

        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def CalcNumStrataRetainedUpperBound(
        self: 'StratumRetentionPredicateStochastic',
        num_strata_deposited: int,
    ) -> int:
        """At most, how many strata are retained after n deposted? Inclusive."""

        return num_strata_deposited

    def CalcMrcaUncertaintyUpperBound(
        self: 'StratumRetentionPredicateStochastic',
        *,
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
        actual_rank_of_mrca: typing.Optional[int]=None,
    ) -> int:
        """At most, how much uncertainty to estimate rank of MRCA? Inclusive."""

        return max(
            first_num_strata_deposited,
            second_num_strata_deposited,
        )
