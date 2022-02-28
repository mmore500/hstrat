import math
import typing


class StratumRetentionPredicateFixedResolution:
    """Functor to implement the fixed resolution stratum retention policy, for
    use with HereditaryStratigraphicColumn.

    This functor enacts the fixed resolution policy by specifying
    whether a stratum with deposition rank r should be retained within the
    hereditary stratigraphic column after n strata have been deposited.

    The fixed resolution policy ensures estimates of MRCA rank will have
    uncertainty bounds less than or equal a fixed, absolute user-specified cap
    that is independent of the number of strata deposited on either column.
    Thus, MRCA rank estimate uncertainty scales as O(1) with respect to the
    greater number of strata deposited on either column.

    Under the fixed resolution policy, the number of strata retained (i.e.,
    space complexity) scales as O(n) with respect to the number of strata
    deposited.

    See Also
    --------
    StratumRetentionCondemnerFixedResolution:
        For a potentially more computationally efficient specificiation of the
        fixed resolution policy that directly generates the ranks of strata
        that should be purged during the nth stratum deposition.
    """

    _fixed_resolution: int

    def __init__(
        self: 'StratumRetentionPredicateFixedResolution',
        fixed_resolution: int=10
    ):
        """Construct the functor.

        Parameters
        ----------
        fixed_resolution : int, optional
            The rank interval strata should be retained at. The uncertainty of
            MRCA estimates provided under the fixed resolution policy will
            always be strictly less than this cap.
        """

        assert fixed_resolution > 0
        self._fixed_resolution = (
            fixed_resolution
        )

    def __eq__(
        self: 'StratumRetentionPredicateFixedResolution',
        other: 'StratumRetentionPredicateFixedResolution',
    ) -> bool:
        """Compare for value-wise equality."""

        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __call__(
        self: 'StratumRetentionPredicateFixedResolution',
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

        This functor's retention policy implementation guarantees that columns
        will retain appropriate strata so that for any two columns with m and n
        strata deposited, the rank of the most recent common ancestor can be
        determined with uncertainty of at most fixed_resolution.

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

        return (
            stratum_rank == num_stratum_depositions_completed
            or stratum_rank % self._fixed_resolution == 0
        )

    def CalcNumStrataRetainedExact(
        self: 'StratumRetentionPredicateFixedResolution',
        num_strata_deposited: int,
    ) -> int:
        """Exactly how many strata are retained after n deposted?"""

        if num_strata_deposited == 0: return 0

        uncertainty = self._fixed_resolution
        newest_stratum_rank = num_strata_deposited - 1
        # +1 for 0'th rank stratum
        num_strata_at_uncertainty_intervals \
            = newest_stratum_rank // uncertainty + 1
        newest_stratum_distinct_from_uncertainty_intervals \
            = (newest_stratum_rank % uncertainty != 0)
        return (
            num_strata_at_uncertainty_intervals
            + newest_stratum_distinct_from_uncertainty_intervals
        )


        if num_strata_deposited <= 2: return num_strata_deposited
        else:
            return (num_strata_deposited - 2) // self._fixed_resolution + 2

    def CalcNumStrataRetainedUpperBound(
        self: 'StratumRetentionPredicateFixedResolution',
        num_strata_deposited: int,
    ) -> int:
        """At most, how many strata are retained after n deposted? Inclusive."""

        return self.CalcNumStrataRetainedExact(
            num_strata_deposited,
        )

    def CalcMrcaUncertaintyUpperBound(
        self: 'StratumRetentionPredicateFixedResolution',
        *,
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
        actual_rank_of_mrca: typing.Optional[int]=None,
    ) -> int:
        """At most, how much uncertainty to estimate rank of MRCA? Inclusive."""

        return self._fixed_resolution

    def CalcRankAtColumnIndex(
        self: 'StratumRetentionPredicateFixedResolution',
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

        # upper bound implementation gives the exact number of strata retained
        if index == self.CalcNumStrataRetainedUpperBound(num_strata_deposited):
            # in-progress deposition case
            return num_strata_deposited
        else:
            return min(
                index * self._fixed_resolution,
                num_strata_deposited - 1,
            )
