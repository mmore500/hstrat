import typing


class StratumRetentionPredicatePerfectResolution:
    """Functor to implement the perfect resolution stratum retention policy, for
    use with HereditaryStratigraphicColumn.

    This functor enacts the perfect resolution policy by specifying
    whether a stratum with deposition rank r should be retained within the
    hereditary stratigraphic column after n strata have been deposited.

    The perfect resolution policy retains all strata. So, comparisons between
    two columns under this policy will detect MRCA rank with zero
    uncertainty. So, MRCA rank estimate uncertainty scales as O(1) with respect
    to the greater number of strata deposited on either column.

    Under the perfect resolution policy, the number of strata retained (i.e.,
    space complexity) scales as O(n) with respect to the number of strata
    deposited.

    See Also
    --------
    StratumRetentionCondemnerPerfectResolution:
        For a potentially more computationally efficient specificiation of the
        perfect resolution policy that directly generates the ranks of strata
        that should be purged during the nth stratum deposition.
    """

    def __call__(
        self: 'StratumRetentionPredicatePerfectResolution',
        stratum_rank: typing.Optional[int]=None,
        num_stratum_depositions_completed: typing.Optional[int]=None,
    ) -> bool:
        """Decide if a stratum within the stratagraphic column should be
        retained or purged.

        Every time a new stratum is deposited, this method is called on each
        stratum present in a HereditaryStratigraphicColumn to determine whether
        it should be retained. Strata that return False are immediately purged
        from the column, meaning that for a stratum to persist it must earn a
        True result from this method each and every time a new stratum is
        deposited.

        This functor's retention policy implementation guarantees that columns
        will retain all strata so that for any two columns with m and n
        strata deposited, the rank of the most recent common ancestor can be
        determined with perfect certainty.

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

        return True

    def __eq__(
        self: 'StratumRetentionPredicatePerfectResolution',
        other: 'StratumRetentionPredicatePerfectResolution',
    ) -> bool:
        """Compare for value-wise equality."""

        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def CalcNumStrataRetainedExact(
        self: 'StratumRetentionPredicatePerfectResolution',
        num_strata_deposited: int,
    ) -> int:
        """Exactly how many strata are retained after n deposted?"""

        return num_strata_deposited

    def CalcNumStrataRetainedUpperBound(
        self: 'StratumRetentionPredicatePerfectResolution',
        num_strata_deposited: int,
    ) -> int:
        """At most, how many strata are retained after n deposted? Inclusive."""

        return self.CalcNumStrataRetainedExact(
            num_strata_deposited=num_strata_deposited,
        )

    def CalcMrcaUncertaintyUpperBound(
        self: 'StratumRetentionPredicatePerfectResolution',
        *,
        first_num_strata_deposited: typing.Optional[int]=None,
        second_num_strata_deposited: typing.Optional[int]=None,
        actual_rank_of_mrca: typing.Optional[int]=None,
    ) -> int:
        """At most, how much uncertainty to estimate rank of MRCA? Inclusive."""

        return 0

    def CalcRankAtColumnIndex(
        self: 'StratumRetentionPredicatePerfectResolution',
        index: int,
        num_strata_deposited: typing.Optional[int]=None,
    ) -> int:
        """After n strata have been deposited, what will the rank of the
        stratum at column index k be?

        Enables a HereditaryStratigraphicColumn using this predicate to
        optimize away storage of rank annotations on strata. Takes into the
        account the possiblity for in-progress stratum depositions that haven't
        been reflected in num_strata_deposited.
        """

        return index
