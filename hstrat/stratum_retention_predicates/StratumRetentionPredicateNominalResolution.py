import typing


class StratumRetentionPredicateNominalResolution:
    """Functor to implement the nominal resolution strata retention policy, for
    use with HereditaryStratigraphicColumn.

    This functor enacts the nominal resolution policy by specifying
    whether a stratum with deposition rank r should be retained within the
    hereditary stratigraphic column after n strata have been deposited.

    The nominal resolution policy only retains the most ancient (i.e., very
    first) and most recent (i.e., last) strata. So, comparisons between two
    columns under this policy will only be able to detect whether they share
    any common ancestor and whether they are from the same organism (i.e., no
    generations have elapsed since the MRCA). Thus, MRCA rank estimate
    uncertainty scales as O(n) with respect to the greater number of strata deposited on either column.

    Under the nominal resolution policy, the number of strata retained (i.e.,
    space complexity) scales as O(1) with respect to the number of strata
    deposited.
    """

    def __call__(
        self: 'StratumRetentionPredicateNominalResolution',
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

        This functor implements the nominal retention policy where only the most
        ancient and most recent strata are retained.

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

        return stratum_rank in (0, num_stratum_depositions_completed)

    def __eq__(
        self: 'StratumRetentionPredicateNominalResolution',
        other: 'StratumRetentionPredicateNominalResolution',
    ) -> bool:
        """Compare for value-wise equality."""

        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def CalcNumStrataRetainedExact(
        self: 'StratumRetentionPredicateNominalResolution',
        num_strata_deposited: int,
    ) -> int:
        """Exactly how many strata are retained after n deposted?"""

        return min(num_strata_deposited, 2)

    def CalcNumStrataRetainedUpperBound(
        self: 'StratumRetentionPredicateNominalResolution',
        num_strata_deposited: typing.Optional[int]=None,
    ) -> int:
        """At most, how many strata are retained after n deposted? Inclusive."""
        return 2

    def CalcMrcaUncertaintyUpperBound(
        self: 'StratumRetentionPredicateNominalResolution',
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

    def CalcRankAtColumnIndex(
        self: 'StratumRetentionPredicateNominalResolution',
        index: int,
        num_strata_deposited: int,
    ) -> int:
        """After n strata have been deposited, what will the rank of the
        stratum at column index k be?

        Enables a HereditaryStratigraphicColumn using this predicate to
        optimize away storage of rank annotations on strata. Takes into the
        account the possiblity for in-progress stratum depositions that haven't
        been reflected in num_strata_deposited.
        """

        return [
            0,
            num_strata_deposited - 1,
            num_strata_deposited,
        ][index]
