import gmpy
import math
import typing


class StratumRetentionPredicateRecencyProportionalResolution:
    """Functor to implement the MRCA-recency-proportional resolution stratum
    retention policy, for use with HereditaryStratigraphicColumn.

    This functor enacts the MRCA-recency-proportional resolution policy by
    specifying whether a stratum with deposition rank r should be retained
    within the hereditary stratigraphic column after n strata have been
    deposited.

    The MRCA-recency-proportional resolution policy ensures estimates of MRCA
    rank will have uncertainty bounds less than or equal to a user-specified
    proportion of the actual number of generations elapsed since the MRCA and
    the deepest of the compared columns. MRCA rank estimate uncertainty scales
    in the worst case scales as O(n) with respect to the greater number of
    strata deposited on either column. However, with respect to estimating the rank of the MRCA when lineages diverged any fixed number of generations ago,
    uncertainty scales as O(1).

    Under the MRCA-recency-proportional resolution policy, the number of strata
    retained (i.e., space complexity) scales as O(log(n)) with respect to the
    number of strata deposited.

    See Also
    --------
    StratumRetentionCondemnerRecencyProportionalResolution:
        For a potentially more computationally efficient specificiation of the
        MRCA-recency-proportional resolution policy that directly generates the
        ranks of strata that should be purged during the nth stratum deposition.
    """

    _guaranteed_mrca_recency_proportional_resolution: int

    def __init__(
        self: 'StratumRetentionPredicateRecencyProportionalResolution',
        guaranteed_mrca_recency_proportional_resolution: int=10,
    ):
        """Construct the functor.

        Parameters
        ----------
        guaranteed_mrca_recency_proportional_resolution : int, optional
            The desired minimum number of intervals between the MRCA and the
            deeper compared column to be able to be distinguished between. The
            uncertainty of MRCA rank estimates provided under the MRCA-recency-
            proportional resolution policy will scale as the actual
            phylogenetic depth of the MRCA divided by
            guaranteed_mrca_recency_proportional_resolution.
        """

        self._guaranteed_mrca_recency_proportional_resolution = (
            guaranteed_mrca_recency_proportional_resolution
        )

    def __eq__(
        self: 'StratumRetentionPredicateRecencyProportionalResolution',
        other: 'StratumRetentionPredicateRecencyProportionalResolution',
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
        """When n strata have been deposited, how big will the interval until
        the first retained stratum be?"""
        resolution = self._guaranteed_mrca_recency_proportional_resolution

        max_uncertainty = num_stratum_depositions_completed // (resolution + 1)
        # round down to lower or equal power of 2
        provided_uncertainty_exp = (max_uncertainty // 2).bit_length()
        provided_uncertainty = 2 ** provided_uncertainty_exp
        return provided_uncertainty

    def __call__(
        self: 'StratumRetentionPredicateRecencyProportionalResolution',
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
        strata deposited, the rank of the most recent common ancestor at rank k
        can be determined with uncertainty of at most

            bound = floor(
                max(m - k, n - k)
                / guaranteed_mrca_recency_proportional_resolution
            )

        ranks.

        How does the predicate work and how does it guarantee this resolution?

        To begin, let's consider setting up just the *first* rank of the
        stratum after the root ancestor we will retain.

        root ancestor                                     extant individual
        |                                                                 |
        |                    num_strata_deposited                         |
        | ___________________________/\_________________________________  |
        |/                                                               \|
        |-------------------|#############################################|
         \_______  ________/|\____________________  ______________________/
                 \/         |                     \/
           max_uncertainty  |            worst_case_mrca_depth
                            |
                            proposed retention rank

        To provide guaranteed resolution, max_uncertainty must be leq than

           worst_case_mrca_depth // guaranteed_resolution

        So, to find the largest permissible max_uncertainty we must solve

           max_uncertainty = worst_case_mrca_depth // guaranteed_resolution

        By construction we have

           worst_case_mrca_depth = num_strata_deposited - max_uncertainty

        Substituting into the above expression gives

           max_uncertainty
           = (num_strata_deposited - max_uncertainty) // guaranteed_resolution

        Solving for max_uncertainty yields

          max_uncertainty
          = num_strata_deposited // (guaranteed_resolution + 1)

        We now have an upper bound for the rank of the first stratum rank
        we must retain. We can repeat this process recursively to select
        ranks that give adequate resolution proportional to
        worst_case_mrca_depth.

        However, we must guarantee that thes ranks are actually available for
        us to retain (i.e., it hasn't been purged out of the column at a
        previous time point as the column was grown by successive deposition).
        We will do this by picking the rank that is the highest power of 2
        less than or equal to our bound. If we repeat this procedure as we
        recurse, we are guaranteed that this rank will have been preserved
        across all previous timepoints.

        This is because a partial sum sequence where all elements are powers
        of 2 and elements in the sequence are will include all multiples of
        powers of 2 greater than or equal to the first element that are less
        than or equal to the sum of the entire
        sequence.

        An example is the best way to convince yourself. Thinking analogously
        in base 10,

           100 + 10... + 1...

        the partial sums of any sequence of this form will always include all
        multiples of powers of 100, 1000, etc. that are less than or equal to
        the sum of the entire sequence.

        In our application, partial sums represent retained ranks. So, all
        ranks that are perfect powers of 2 measuring from the root ancestor
        will have been retained after being deposited. This property
        generalizes recursively.

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

        resolution = self._guaranteed_mrca_recency_proportional_resolution

        # to satisfy requirements of HereditaryStratigraphicColumn impl
        # we must always keep root ancestor and newest stratum
        if (stratum_rank in (0, num_stratum_depositions_completed)): return True
        elif num_stratum_depositions_completed <= resolution: return True

        provided_uncertainty = self._calc_provided_uncertainty(
            num_stratum_depositions_completed,
        )

        # logically,  we could just test
        #   if stratum_rank == provided_uncertainty: return True
        # but we are guaranteed to eventually return True under the weaker
        # condition
        #   if stratum_rank % provided_uncertainty == 0
        # so as an optimization go ahead and return True now if it holds
        if stratum_rank % provided_uncertainty == 0: return True
        elif stratum_rank < provided_uncertainty: return False
        else: return self.__call__(
            stratum_rank - provided_uncertainty,
            num_stratum_depositions_completed - provided_uncertainty,
        )

    def CalcNumStrataRetainedExact(
        self: 'StratumRetentionPredicateRecencyProportionalResolution',
        num_strata_deposited: int,
    ) -> int:
        """Exactly how many strata are retained after n deposted?

        The calculation can be written mathematically as,

          weight of binary expansion of n (i.e., #1's set in binary repr)
          + sum(
              floor( log2(n//r) )
              for r from 1 to r inclusive
          )
          + 1

        where

          n = num_strata_deposited - 1
          r = resolution

        This expression for exact number deposited was extrapolated from
            * resolution = 0, <https://oeis.org/A063787>
            * resolution = 1, <https://oeis.org/A056791>
        and is unit tested extensively.

        Note that the implementation must include a special case to account for
        n < r causing log2(0). In this case, the number of strata retained is
        equal to the number deposited (i.e., none have been discarded yet).
        """

        resolution = self._guaranteed_mrca_recency_proportional_resolution
        if num_strata_deposited - 1 <= resolution: return num_strata_deposited
        else: return (
            gmpy.popcount(num_strata_deposited - 1)
            + sum(
                # X.bit_length() - 1 equivalent to floor(log2(X))
                ((num_strata_deposited - 1) // r).bit_length() - 1
                for r in range(1, resolution + 1)
            )
            + 1
        )

    def CalcNumStrataRetainedUpperBound(
        self: 'StratumRetentionPredicateRecencyProportionalResolution',
        num_strata_deposited: int,
    ):
        """At most, how many strata are retained after n deposted? Inclusive."""

        return self.CalcNumStrataRetainedExact(
            num_strata_deposited=num_strata_deposited,
        )

    def CalcMrcaUncertaintyUpperBound(
        self: 'StratumRetentionPredicateRecencyProportionalResolution',
        *,
        actual_rank_of_mrca: int,
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
    ) -> int:
        """At most, how much uncertainty to estimate rank of MRCA? Inclusive."""

        max_ranks_since_mrca = max(
            first_num_strata_deposited,
            second_num_strata_deposited,
        ) - actual_rank_of_mrca
        if self._guaranteed_mrca_recency_proportional_resolution == 0:
            return min(first_num_strata_deposited, second_num_strata_deposited)
        else: return (
            max_ranks_since_mrca
            // self._guaranteed_mrca_recency_proportional_resolution
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

        resolution = self._guaranteed_mrca_recency_proportional_resolution

        # calculate the interval between retained strata we're starting out with
        # -1 due to *lack* of an in-progress deposition
        provided_uncertainty = self._calc_provided_uncertainty(
            num_strata_deposited - 1,
        )
        # we could just take a simple recursive approach like this
        #
        #   if index == 0: return 0
        #   else: return provided_uncertainty + self.CalcRankAtColumnIndex(
        #       index - 1,
        #       num_strata_deposited - provided_uncertainty,
        #   )
        #
        # but as an optimization, we should take as many steps as possible at
        # the current uncertainty interval size stage before recursing down to
        # the next half-as-small uncertainty interval size

        # calculate the greatest rank at which that interval is viable
        # i.e., where max_uncertainty == provided_uncertainty... we must solve
        #
        #   provided_uncertainty = least_num_strata // (resolution + 1)
        #
        # and
        #
        #   least_num_strata = num_strata_deposited - greatest_viable_rank

        # -1 due to *lack* of an in-progress deposition
        greatest_viable_rank = (
            num_strata_deposited - 1
            - provided_uncertainty * (resolution + 1)
        )

        # calculate how many steps at provided_uncertainty interval we can take
        # +provided_uncertainty because greatest viable rank is the *last*
        # position we can take a step in our interval from
        num_interval_steps = (
            (greatest_viable_rank + provided_uncertainty)
            // provided_uncertainty
        )

        if index <= num_interval_steps or provided_uncertainty == 1:
            # we can reach index within the current provided_uncertainty stage
            # note: must always enter base case when provided uncertainty is 1
            # or infinite recursion will result
            return index * provided_uncertainty
        else:
            # take as many index steps as possible at current uncertainty stage
            # and add number of ranks accrued at subsequent uncertainty stages
            num_ranks_traversed = num_interval_steps * provided_uncertainty
            return num_ranks_traversed + self.CalcRankAtColumnIndex(
                index=index - num_interval_steps,
                num_strata_deposited
                    =num_strata_deposited - num_ranks_traversed,
            )
