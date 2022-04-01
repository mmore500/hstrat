import gmpy
import math
import typing


class StratumRetentionPredicateSpaceFillApproxRecencyProportionalResolution:
    """Functor to implement the approximate space-filling MRCA-recency-
    proportional resolution stratum retention policy, for use with
    HereditaryStratigraphicColumn.

    This functor enacts the approximate space-filling MRCA-recency-proportional
    resolution policy by specifying whether a stratum with deposition rank r
    should be retained within the hereditary stratigraphic column after n
    strata have been deposited.

    The approximate space-filling MRCA-recency-proportional resolution policy imposes an O(1) limit on the number of retained strata and that retained strata will be exponentially distributed with respect to ranks elapsed since their deposit. MRCA rank estimate uncertainty scales in the worst case scales as O(n) with respect to the greater number of strata deposited on either column. However, with respect to estimating the rank of the MRCA when lineages diverged any fixed number of generations ago,
    uncertainty scales as O(log(n)) (TODO check this).

    Under the MRCA-recency-proportional resolution policy, the number of strata
    retained (i.e., space complexity) scales as O(1) with respect to the
    number of strata deposited.

    Suppose k is specified as the policy's target space utilization. The first
    k strata deposited are retained. Then, strata are retained so that MRCA
    rank estimate uncertainty is less than or equal to s * (1 - n^(-1/k))
    is the number of strata deposited and s is the true number of ranks
    deposited since the MRCA. From this point onward, the number of strata
    retained fluctuates between respects a hard upper limit of 4k + 2
    (inclusive). All strata are retained until the target space utilization is
    reached, then the number of strata retained fluctuates to maintain the
    guaranteed estimate uncertainty. For larger target space utilizations,
    number of strata retained appears generally less than twice the target
    space utilization.

    See Also
    --------
    StratumRetentionPredicateSpaceCapExactRecencyProportionalResolution
    StratumRetentionPredicateSpaceFillApproxRecencyProportionalResolution
    StratumRetentionPredicateSpaceFillExactRecencyProportionalResolution
    """

    _target_size: int

    def __init__(
        self: \
        'StratumRetentionPredicateSpaceFillApproxRecencyProportionalResolution',
        target_size: int=100,
    ):
        """Construct the functor.

        Parameters
        ----------
        target_size : int, optional
            Target column size. Must be >= 8 (TODO relax?).
        """

        assert target_size >= 8
        self._target_size = target_size

    def __eq__(
        self: \
        'StratumRetentionPredicateSpaceFillApproxRecencyProportionalResolution',
        other: \
        'StratumRetentionPredicateSpaceFillApproxRecencyProportionalResolution',
    ) -> bool:
        """Compare for value-wise equality."""

        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def _calc_base(
        self: \
        'StratumRetentionPredicateSpaceFillApproxRecencyProportionalResolution',
        num_strata_deposited: int,
    ) -> float:
        """What should the base of the exponential distribution of retained
        ranks be?"""

        # base ** target_size == num_strata_deposited
        # take the target_size'th root of each side...
        return num_strata_deposited ** (1 / self._target_size)

    def _calc_max_permissible_uncertainty(
        self: \
        'StratumRetentionPredicateSpaceFillApproxRecencyProportionalResolution',
        num_strata_deposited: int,
        rank: int,
    ) -> int:
        """After n strata have been deposited, at most how many ranks can be
        spaced between retained strata surrounding rank r?
        """

        ranks_since = num_strata_deposited - rank
        base = self._calc_base(num_strata_deposited)

        # aka
        # base ** log(ranks_since, base) - base ** (log(ranks_since, base) - 1)
        max_uncertainty = ranks_since - ranks_since / base

        # round down to lower or equal power of 2
        max_permissible_uncertainty_exp \
            = (int(max_uncertainty) // 2).bit_length()
        max_permissible_uncertainty = 2 ** max_permissible_uncertainty_exp

        assert max_permissible_uncertainty > 0

        return max_permissible_uncertainty

    def _calc_provided_uncertainty(
        self: \
        'StratumRetentionPredicateSpaceFillApproxRecencyProportionalResolution',
        num_strata_deposited: int,
        rank: int,
    ) -> int:
        """After n strata have been deposited, how many ranks are spaced
        between retained strata at rank r?

        Uncertainty is chosen so that, in the worst case, the "front" rank that
        is "uncertainty" # of ranks ahead of the provided "back" rank has max
        permissible uncertainty greater than or equal to the provided
        uncertainty.

        Note that the returned value actually corresponds to one more than the
        uncertainty with respect to calculating MRCA supposing two identically
        distributed columns. For example a return value of 1 corresponds to
        strata retained at every rank, so the rank of the MRCA can be
        determined with 0 uncertainty.
        """

        # ansatz
        provided_uncertainty = self._calc_max_permissible_uncertainty(
            num_strata_deposited,
            rank,
        )

        # apply correction to accomodate uncertainty requirement of worst-case
        # captured rank, if needed
        if self._calc_max_permissible_uncertainty(
            num_strata_deposited,
            rank + provided_uncertainty,
        ) < provided_uncertainty:
            # TODO
            # prove that we at most have to divide by 2,
            # i.e., that rank + ansatz / 2 cannot require uncertainty less than
            # ansatz / 2
            provided_uncertainty //= 2

        # sanity check: are we satisfying uncertainty requirements of
        # worst-case captured rank?
        assert self._calc_max_permissible_uncertainty(
            num_strata_deposited,
            rank + provided_uncertainty,
        ) >= provided_uncertainty
        # max "uncertainty" is 1 where every strata retained
        assert provided_uncertainty > 0

        return provided_uncertainty

    def __call__(
        self: \
        'StratumRetentionPredicateSpaceFillApproxRecencyProportionalResolution',
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

        # to satisfy requirements of HereditaryStratigraphicColumn impl
        # we must always keep root ancestor and newest stratum
        if (stratum_rank in (0, num_stratum_depositions_completed)): return True
        elif num_stratum_depositions_completed < self._target_size: return True

        cur_rank = 0
        while cur_rank < stratum_rank:
            # +1 due to in-progress deposition
            provided_uncertainty = self._calc_provided_uncertainty(
                num_stratum_depositions_completed + 1,
                cur_rank,
            )

            cur_rank += provided_uncertainty

        return cur_rank == stratum_rank

    def CalcNumStrataRetainedExact(
        self: 'StratumRetentionPredicateSpaceFillApproxRecencyProportionalResolution',
        num_strata_deposited: int,
    ) -> int:
        """Exactly how many strata are retained after n deposted?"""

        if num_strata_deposited <= self._target_size:
            return num_strata_deposited

        cur_rank = 0
        counter = 0
        while cur_rank < num_strata_deposited:
            provided_uncertainty = self._calc_provided_uncertainty(
                num_strata_deposited,
                cur_rank,
            )
            cur_rank += provided_uncertainty
            counter += 1

        return counter

    def CalcNumStrataRetainedUpperBound(
        self: 'StratumRetentionPredicateSpaceFillApproxRecencyProportionalResolution',
        num_strata_deposited: int,
    ):
        """At most, how many strata are retained after n deposted? Inclusive."""

        return 2 * num_strata_deposited + 2

    def CalcMrcaUncertaintyUpperBound(
        self: 'StratumRetentionPredicateSpaceFillApproxRecencyProportionalResolution',
        *,
        actual_rank_of_mrca: int,
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
    ) -> int:
        """At most, how much uncertainty to estimate rank of MRCA? Inclusive."""

        max_num_strata_deposited = max(
            first_num_strata_deposited,
            second_num_strata_deposited,
        )
        max_ranks_since_mrca = max_num_strata_deposited - actual_rank_of_mrca
        base = self._calc_base(max_num_strata_deposited)

        return int(
            max_ranks_since_mrca * (1.0 - 1.0 / base)
        )

    def CalcRankAtColumnIndex(
        self: 'StratumRetentionPredicatePerfectResolution',
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

        cur_rank = 0
        counter = 0
        while counter < index:
            if cur_rank < num_strata_deposited:
                provided_uncertainty = self._calc_provided_uncertainty(
                    num_stratum_depositions_completed,
                    cur_rank,
                )
                cur_rank += provided_uncertainty
            else:
                # in-progress stratum deposition case
                assert counter == index - 1
                cur_rank += 1
                assert cur_rank == num_strata_deposited
            counter += 1

        return cur_rank
