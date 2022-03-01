import math
import typing


class StratumRetentionPredicateDepthProportionalResolution:
    """Functor to implement the depth-proportional resolution stratum retention
    policy, for use with HereditaryStratigraphicColumn.

    This functor enacts the depth-proportional resolution policy by specifying
    whether a stratum with deposition rank r should be retained within the
    hereditary stratigraphic column after n strata have been deposited.

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
    StratumRetentionCondemnerDepthProportionalResolution:
        For a potentially more computationally efficient specificiation of the
        depth-proportional resolution policy that directly generates the ranks
        of strata that should be purged during the nth stratum deposition.
    StratumRetentionPredicateTaperedDepthProportionalResolution:
        For a predicate retention policy that achieves the same guarantees for
        depth-proportional resolution but purges unnecessary strata more
        graudally.
    """

    _guaranteed_depth_proportional_resolution: int

    def __init__(
        self: 'StratumRetentionPredicateDepthProportionalResolution',
        guaranteed_depth_proportional_resolution: int=10
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

        assert guaranteed_depth_proportional_resolution > 0
        self._guaranteed_depth_proportional_resolution = (
            guaranteed_depth_proportional_resolution
        )

    def __eq__(
        self: 'StratumRetentionPredicateDepthProportionalResolution',
        other: 'StratumRetentionPredicateDepthProportionalResolution',
    ) -> bool:
        """Compare for value-wise equality."""

        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def _calc_provided_uncertainty(
        self: 'StratumRetentionPredicateDepthProportionalResolution',
        num_stratum_depositions_completed: int,
    ) -> int:
        """After n strata have been deposited, how many ranks are spaced
        between retained strata?"""

        guaranteed_resolution = self._guaranteed_depth_proportional_resolution
        max_uncertainty \
            = num_stratum_depositions_completed // guaranteed_resolution

        # round down to lower or equal power of 2
        provided_uncertainty_exp = (max_uncertainty // 2).bit_length()
        provided_uncertainty = 2 ** provided_uncertainty_exp
        return provided_uncertainty

    def __call__(
        self: 'StratumRetentionPredicateDepthProportionalResolution',
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
        determined with uncertainty of at most

            bound = floor(max(m, n) / guaranteed_depth_proportional_resolution)

        ranks. Achieving this limit on uncertainty requires retaining sufficient
        strata so that no more than bound ranks elapsed between any two strata.
        This policy accumulates retained strata at a fixed interval until twice
        as many as guaranteed_depth_proportional_resolution are at hand. Then,
        every other retained stratum is purged and the cycle repeats with a new
        twice-as-wide interval between retained strata.

        Suppose guaranteed_depth_proportional_resolution is 3.

               guaranteed   actual
        time   resolution   uncertainty   column
        --------------------------------------------------------
        1      0            0             |
        2      0            0             ||
        3      1            0             |||
        4      1            0             ||||
        5      1            0             |||||
        6      2            2             | | ||
        7      2            2             | | | |
        8      2            2             | | | ||
        9      3            2             | | | | |
        10     3            2             | | | | ||
        11     3            2             | | | | | |
        12     4            4             |   |   |  |
        13     4            4             |   |   |   |
        14     4            4             |   |   |   ||
        15     5            4             |   |   |   | |
        16     5            4             |   |   |   |  |
        17     5            4             |   |   |   |   |
        18     6            4             |   |   |   |   ||
        19     6            4             |   |   |   |   | |
        20     6            4             |   |   |   |   |  |
        21     7            4             |   |   |   |   |   |
        22     7            4             |   |   |   |   |   ||
        23     7            4             |   |   |   |   |   | |
        24     8            8             |       |       |      |
        25     8            8             |       |       |       |
        26     8            8             |       |       |       ||
        27     9            8             |       |       |       | |
        28     9            8             |       |       |       |  |
        29     9            8             |       |       |       |   |
        30     10           8             |       |       |       |    |

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

        guaranteed_resolution = self._guaranteed_depth_proportional_resolution

        # easy edge cases we must always retain
        if (
            # always retain newest stratum
            stratum_rank == num_stratum_depositions_completed
            # retain all strata until more than num_intervals are deposited
            or num_stratum_depositions_completed < guaranteed_resolution
        ): return True

        # +1 because of in-progress deposition
        provided_uncertainty = self._calc_provided_uncertainty(
            num_stratum_depositions_completed + 1,
        )
        return stratum_rank % provided_uncertainty == 0

    def CalcNumStrataRetainedExact(
        self: 'StratumRetentionPredicateDepthProportionalResolution',
        num_strata_deposited: int,
    ) -> int:
        """Exactly how many strata are retained after n deposted?"""

        if num_strata_deposited == 0: return 0

        provided_uncertainty = self._calc_provided_uncertainty(
            num_strata_deposited,
        )
        newest_stratum_rank = num_strata_deposited - 1
        # +1 for 0'th rank stratum
        num_strata_at_uncertainty_intervals \
            = newest_stratum_rank // provided_uncertainty + 1
        newest_stratum_distinct_from_uncertainty_intervals \
            = (newest_stratum_rank % provided_uncertainty != 0)
        return (
            num_strata_at_uncertainty_intervals
            + newest_stratum_distinct_from_uncertainty_intervals
        )

    def CalcNumStrataRetainedUpperBound(
        self: 'StratumRetentionPredicateDepthProportionalResolution',
        num_strata_deposited: typing.Optional[int]=None,
    ) -> int:
        """At most, how many strata are retained after n deposted? Inclusive."""

        return self._guaranteed_depth_proportional_resolution * 2 + 1

    def CalcMrcaUncertaintyUpperBound(
        self: 'StratumRetentionPredicateDepthProportionalResolution',
        *,
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
        actual_rank_of_mrca: typing.Optional[int]=None,
    ) -> int:
        """At most, how much uncertainty to estimate rank of MRCA? Inclusive."""

        return max(
            first_num_strata_deposited,
            second_num_strata_deposited,
        ) // self._guaranteed_depth_proportional_resolution


    def _CalcRankAtColumnIndexImpl(
        self: 'StratumRetentionPredicateDepthProportionalResolution',
        index: int,
        num_strata_deposited: int,
    ) -> int:
        """After n strata have been deposited, what will the rank of the
        stratum at column index k be?

        Assumes the no in-progress stratum depositions that haven't been
        reflected in num_strata_deposited.
        """

        provided_uncertainty = self._calc_provided_uncertainty(
            num_strata_deposited,
        )
        return min(
            index * provided_uncertainty,
            num_strata_deposited - 1
        )

    def CalcRankAtColumnIndex(
        self: 'StratumRetentionPredicateDepthProportionalResolution',
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

        # 0th index is always rank 0
        if index == 0: return 0

        prev = self._CalcRankAtColumnIndexImpl(index - 1, num_strata_deposited)
        cur = self._CalcRankAtColumnIndexImpl(index, num_strata_deposited)
        if (cur == prev):
            # in cases where the same rank result is calculated for this index
            # and preceding index, the current index is an in-progress
            # deposition and must be calculated as the rank succeeding the
            # previous stratum's rank
            return prev + 1
        else:
            return cur
