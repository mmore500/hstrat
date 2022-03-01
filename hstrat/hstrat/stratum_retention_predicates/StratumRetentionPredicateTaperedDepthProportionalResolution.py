import math
import typing


class StratumRetentionPredicateTaperedDepthProportionalResolution:
    """Functor to implement the tapered depth-proportional resolution stratum
    retention policy, for use with HereditaryStratigraphicColumn.

    This functor enacts the tapered depth-proportional resolution policy by
    specifying whether a stratum with deposition rank r should be retained
    within the hereditary stratigraphic column after n strata have been
    deposited.

    The tapered depth-proportional resolution policy ensures estimates of MRCA
    rank will have uncertainty bounds less than or equal to a user-specified
    proportion of the largest number of strata deposited on either column.
    Thus, MRCA rank estimate uncertainty scales as O(n) with respect to the
    greater number of strata deposited on either column.

    Under the tapered depth-proportional resolution policy, the number of strata
    retained (i.e., space complexity) scales as O(1) with respect to the number
    of strata deposited.

    See Also
    --------
    StratumRetentionCondemnerTaperedDepthProportionalResolution:
        For a potentially more computationally efficient specificiation of the
        depth-proportional resolution policy that directly generates the ranks
        of strata that should be purged during the nth stratum deposition.
    StratumRetentionPredicateDepthProportionalResolution:
        For a predicate retention policy that achieves the same guarantees for
        depth-proportional resolution but purges unnecessary strata more
        aggressively and abruptly.
    """

    _guaranteed_depth_proportional_resolution: int

    def __init__(
        self: 'StratumRetentionPredicateTaperedDepthProportionalResolution',
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
        self: 'StratumRetentionPredicateTaperedDepthProportionalResolution',
        other: 'StratumRetentionPredicateTaperedDepthProportionalResolution',
    ) -> bool:
        """Compare for value-wise equality."""

        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def _calc_provided_uncertainty(
        self: 'StratumRetentionPredicateTaperedDepthProportionalResolution',
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
        self: 'StratumRetentionPredicateTaperedDepthProportionalResolution',
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
        every other retained stratum is purged gradually from back to front
        until the cycle repeats with a new twice-as-wide interval between
        retained strata.

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
        cur_stage_uncertainty = self._calc_provided_uncertainty(
            num_stratum_depositions_completed + 1,
        )
        cur_stage_idx = stratum_rank // cur_stage_uncertainty
        cur_stage_max_idx = \
            num_stratum_depositions_completed // cur_stage_uncertainty

        # use lambdas to prevent division by zero
        prev_stage_uncertainty = cur_stage_uncertainty // 2
        prev_stage_idx = lambda: stratum_rank // prev_stage_uncertainty
        prev_stage_max_idx = \
            lambda: num_stratum_depositions_completed // prev_stage_uncertainty

        return (
            stratum_rank % cur_stage_uncertainty == 0
            or (
                stratum_rank % prev_stage_uncertainty == 0
                and prev_stage_idx()
                    > 2 * prev_stage_max_idx()
                        - 4 * guaranteed_resolution
                        + 1
            )
        )

    def CalcNumStrataRetainedExact(
        self: 'StratumRetentionPredicateTaperedDepthProportionalResolution',
        num_strata_deposited: int,
    ) -> int:
        """Exactly how many strata are retained after n deposted?"""

        guaranteed_resolution = self._guaranteed_depth_proportional_resolution

        if num_strata_deposited < guaranteed_resolution * 2 + 1:
            return num_strata_deposited
        else:
            # must calculate whether there will be +1 due to retention of
            # most recently deposited stratum
            # (i.e., whether it overlaps with a rank from among
            # the 2 * resolution pegs)
            subtrahend = 2 * guaranteed_resolution + 1
            shifted = num_strata_deposited - subtrahend
            divisor = 2 * guaranteed_resolution - 1
            # equivalent int(math.floor(math.log(shifted // divisor + 1, 2)))
            exp = (shifted // divisor + 1).bit_length() - 1
            modulus = 2**exp
            bump = (num_strata_deposited - 1) % modulus != 0

            return 2 * guaranteed_resolution + bump

    def CalcNumStrataRetainedUpperBound(
        self: 'StratumRetentionPredicateTaperedDepthProportionalResolution',
        num_strata_deposited: typing.Optional[int]=None,
    ) -> int:
        """At most, how many strata are retained after n deposted? Inclusive."""

        return self._guaranteed_depth_proportional_resolution * 2 + 1

    def CalcMrcaUncertaintyUpperBound(
        self: 'StratumRetentionPredicateTaperedDepthProportionalResolution',
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
