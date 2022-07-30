from collections import OrderedDict
import functools
import interval_search as inch
import itertools as it
import math
import mpmath as mp
import numpy as np
import typing
import warnings

from ...helpers import bit_floor, div_range, is_nondecreasing, memoize_generator


class StratumRetentionPredicateTaperedGeomSeqNthRoot:
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
    """

    _degree: int
    _interspersal: int

    def __init__(
        self: 'StratumRetentionPredicateTaperedGeomSeqNthRoot',
        degree: int=100,
        interspersal: int=2,
    ):
        """Construct the functor.

        Parameters
        ----------
        degree : int, optional
            TODO.
        interspersal : int, optional
            TODO.
        """

        assert degree >= 0
        assert interspersal >= 1
        self._degree = degree
        self._interspersal = interspersal

    def __eq__(
        self: 'StratumRetentionPredicateTaperedGeomSeqNthRoot',
        other: 'StratumRetentionPredicateTaperedGeomSeqNthRoot',
    ) -> bool:
        """Compare for value-wise equality."""

        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def _calc_common_ratio(
        self: 'StratumRetentionPredicateTaperedGeomSeqNthRoot',
        num_strata_deposited: int,
    ) -> float:
        """What should the base of the exponential distribution of retained
        ranks be?"""

        # this try-except isn't necessary for the test cases
        # and the bounds of normal usage, but provides better resiliency
        # for extreme magnitude num_strata_deposited which may arise from time
        # to time due to trickle down to this function from within a doubling
        # search
        # the mpf type (artibtrary-precision floating-point) will propagate
        # forward through subsequent computations
        try:
            num_strata_deposited = float(num_strata_deposited)
        except OverflowError:
            warnings.warn(
                'OverflowError converting num_strata_deposited to float, '
                'converting to mpmath.mpf instead.'
            )
            num_strata_deposited = mp.mpf(num_strata_deposited)

        # base ** degree == num_strata_deposited
        # take the degree'th root of each side...
        return num_strata_deposited ** (1 / self._degree)

    def _calc_target_recency(
        self: 'StratumRetentionPredicateTaperedGeomSeqNthRoot',
        pow: int,
        num_strata_deposited: int,
    ) -> float:
        common_ratio = self._calc_common_ratio(num_strata_deposited)
        return common_ratio ** pow

    def _calc_target_rank(
        self: 'StratumRetentionPredicateGeomSeqNthRoot',
        pow: int,
        num_strata_deposited: int,
    ) -> int:
        """TODO."""
        target_recency = self._calc_target_recency(pow, num_strata_deposited)
        recency_cutoff = target_recency
        rank_cutoff = max(
            num_strata_deposited - int(math.ceil(recency_cutoff)),
            0,
        )
        if num_strata_deposited == 0: assert rank_cutoff == 0
        else: assert 0 <= rank_cutoff <= num_strata_deposited - 1
        return rank_cutoff

    def _calc_rank_cutoff(
        self: 'StratumRetentionPredicateGeomSeqNthRoot',
        pow: int,
        num_strata_deposited: int,
    ) -> int:
        """TODO."""
        target_recency = self._calc_target_recency(pow, num_strata_deposited)
        rank_cutoff = max(
            num_strata_deposited - int(math.ceil(
                target_recency
                * (self._interspersal + 1) / self._interspersal
            )),
            0,
        )
        if num_strata_deposited == 0: assert rank_cutoff == 0
        else: assert 0 <= rank_cutoff <= num_strata_deposited - 1
        return rank_cutoff

    def _calc_rank_sep(
        self: 'StratumRetentionPredicateTaperedGeomSeqNthRoot',
        pow: int,
        num_strata_deposited: int,
    ) -> int:
        """TODO."""
        target_recency = self._calc_target_recency(pow, num_strata_deposited)
        # spacing between retained ranks
        target_retained_ranks_sep = max(
            target_recency / self._interspersal,
            1.0,
        )
        # round down to power of 2
        retained_ranks_sep = bit_floor(int(target_retained_ranks_sep))
        return retained_ranks_sep

    def _calc_rank_backstop(
        self: 'StratumRetentionPredicateTaperedGeomSeqNthRoot',
        pow: int,
        num_strata_deposited: int,
    ) -> int:
        """TODO."""

        rank_cutoff = self._calc_rank_cutoff(pow, num_strata_deposited)
        retained_ranks_sep = self._calc_rank_sep(pow, num_strata_deposited)

        # round UP from rank_cutoff
        # adapted from https://stackoverflow.com/a/14092788
        min_retained_rank = (
            rank_cutoff
            - (rank_cutoff % -retained_ranks_sep)
        )
        assert min_retained_rank % retained_ranks_sep == 0

        if num_strata_deposited == 0: assert min_retained_rank == 0
        else: assert 0 <= min_retained_rank <= num_strata_deposited - 1
        return min_retained_rank

    def _get_naive_ranks(
        self: 'StratumRetentionPredicateTaperedGeomSeqNthRoot',
        pow: int,
        num_strata_deposited: int,
    ):

        min_retained_rank = self._calc_rank_backstop(pow, num_strata_deposited)
        retained_ranks_sep = self._calc_rank_sep(pow, num_strata_deposited)

        return set(range(
            min_retained_rank, # start
            num_strata_deposited, # stop
            retained_ranks_sep, # sep
        ))

    def __hash__(self):
        return hash(
            (self._degree, self._interspersal),
        )

    @memoize_generator()
    # note: may return duplicates, but this is ok for use case
    # because priority only depends on soonest position in yield stream
    def _iter_priority_ranks(
        self: 'StratumRetentionPredicateTaperedGeomSeqNthRoot',
        pow: int,
        num_strata_deposited: int,
    ):
        """Iterate over ranks in order of last-to-be-deleted to first-to-be-deleted for a certain pow."""

        if num_strata_deposited == 1:
            yield 0
            return
        assert num_strata_deposited

        min_retained_rank = self._calc_rank_backstop(pow, num_strata_deposited)
        retained_ranks_sep = self._calc_rank_sep(pow, num_strata_deposited)

        if pow == self._degree:
            # the highest-degree pow always tracks strata 0
            # and the biggest relevant sep for strata 0 is infinite.
            # i.e., the backstop for highest-debree pow is always strata 0
            # So, we need a special case for this pow.
            # However, because strata 0 is retained indefinitely, we actually
            # only need to worry about the next retained strata,
            # which is at retained_ranks_sep.
            # Thus, we use calc_rank_sep instead of calc_rank_backstop.
            #TODO can this doubling search be done in constant time?
            biggest_relevant_rank = inch.doubling_search(
                lambda x: self._calc_rank_sep(pow, x+1) >= num_strata_deposited,
                num_strata_deposited,
            )
            biggest_relevant_sep = self._calc_rank_sep(
                pow,
                biggest_relevant_rank,
            )

        else:
            #TODO can this doubling search be done in constant time?
            biggest_relevant_rank = inch.doubling_search(
                lambda x: \
                    self._calc_rank_backstop(pow, x+1) >= num_strata_deposited,
                num_strata_deposited,
            )
            biggest_relevant_sep = self._calc_rank_sep(
                pow,
                biggest_relevant_rank,
            )
            biggest_relevant_sep = retained_ranks_sep * 2

        # in practice, just
        # cur_sep == retained_ranks * 2 seems required
        # i.e., tests pass with
        #
        # for cur_sep in retained_ranks_sep * 2,:
        #
        # TODO can this be proven?
        for cur_sep in div_range(
            biggest_relevant_sep,
            retained_ranks_sep, # non-inclusive
            2,
        ):
            #TODO can this doubling search be done in constant time?
            cur_sep_rank = inch.doubling_search(
                lambda x: self._calc_rank_sep(pow, x) >= cur_sep,
                num_strata_deposited,
            )
            cur_sep_rank_backstop = self._calc_rank_backstop(
                pow,
                cur_sep_rank,
            )

            yield from reversed(range(
                cur_sep_rank_backstop, # start
                # +1 to be inclusive of cur_sep_rank
                min(cur_sep_rank + 1, num_strata_deposited), # stop
                cur_sep, # sep
            ))

        # TODO somehow exclude duplicates with above for better efficiency?
        yield from reversed(range(
            min_retained_rank, # start
            num_strata_deposited, # stop
            retained_ranks_sep, # sep
        ))

        # recurse
        if retained_ranks_sep == 1:
            # base case
            yield from reversed(range(
                0,
                min_retained_rank,
            ))
            return

        prev_sep_rank = inch.binary_search(
            lambda x: \
                self._calc_rank_sep(pow, x + 1) >= retained_ranks_sep,
                0,
                num_strata_deposited - 1,
        )
        yield from range(
            min_retained_rank,
            prev_sep_rank, # not inclusive
            -retained_ranks_sep,
        )
        assert prev_sep_rank < num_strata_deposited
        yield from self._iter_priority_ranks(
            pow,
            # + 1 due to apparent off-by-one error w/ just prev_sep_rank
            # where rank 5984 isn't properly retained
            # with degree 9, interspersal 2 @ generation 6405
            min(prev_sep_rank + 1, num_strata_deposited - 1),
        )

    @functools.lru_cache(maxsize=512)
    def _get_retained_ranks(
        self: 'StratumRetentionPredicateTaperedGeomSeqNthRoot',
        num_strata_deposited: int,
    ) -> typing.Set[int]:
        """TODO."""

        # special case
        if num_strata_deposited == 0: return set()

        interspersal = self._interspersal
        last_rank = num_strata_deposited - 1
        res = {0, last_rank}

        iters = [
            self._iter_priority_ranks(pow, num_strata_deposited)
            # don't iterate over 0th pow, this is just the most recent rank
            # i.e., recency == 1
            for pow in reversed(range(1, self._degree + 1))
        ]
        # round robin, taking at least one from each
        while len(res) < self.CalcNumStrataRetainedUpperBound():
            res_before = len(res)
            for iter_ in iters:
                for priority_rank in iter_:
                    if priority_rank not in res:
                        res.add(priority_rank)
                        break
                if len(res) == self.CalcNumStrataRetainedUpperBound():
                    break
            if res_before == len(res):
                break

        assert all(isinstance(n, int) for n in res)
        assert all(0 <= n < num_strata_deposited for n in res)
        assert len(res) <= self.CalcNumStrataRetainedUpperBound()
        assert res
        return res

    def _iter_retained_ranks(
        self: 'StratumRetentionPredicateTaperedGeomSeqNthRoot',
        num_strata_deposited: int,
    ):
        yield from sorted(self._get_retained_ranks(num_strata_deposited))

    def CalcNumStrataRetainedExact(
        self: 'StratumRetentionPredicateTaperedGeomSeqNthRoot',
        num_strata_deposited: int,
    ) -> int:
        """Exactly how many strata are retained after n deposted?"""

        return min(
            num_strata_deposited,
            self.CalcNumStrataRetainedUpperBound(),
        )

    def __call__(
        self: 'StratumRetentionPredicateTaperedGeomSeqNthRoot',
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

        return stratum_rank in self._get_retained_ranks(
            num_stratum_depositions_completed + 1,
        )

    def CalcNumStrataRetainedExact(
        self: 'StratumRetentionPredicateTaperedGeomSeqNthRoot',
        num_strata_deposited: int,
    ) -> int:
        """Exactly how many strata are retained after n deposted?"""

        return len(
            self._get_retained_ranks(num_strata_deposited)
        )

    def CalcNumStrataRetainedUpperBound(
        self: 'StratumRetentionPredicateTaperedGeomSeqNthRoot',
        num_strata_deposited: typing.Optional[int]=None,
    ):
        """At most, how many strata are retained after n deposted? Inclusive."""

        # +2 is 0th rank and last rank
        return self._degree * 2 * (self._interspersal + 1) + 2

    def CalcMrcaUncertaintyUpperBound(
        self: 'StratumRetentionPredicateTaperedGeomSeqNthRoot',
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
        if max_num_strata_deposited == 0: return 0

        interspersal = self._interspersal
        # edge case: no uncertainty guarantee for interspersal 1
        # interspersal >= 2 required for uncertainty guarantee
        if interspersal == 1: return max_num_strata_deposited

        max_ranks_since_mrca = max_num_strata_deposited - actual_rank_of_mrca
        # edge case: columns are identical
        if max_ranks_since_mrca == 0: return 0

        common_ratio = self._calc_common_ratio(max_num_strata_deposited)
        # edge case: no strata have yet been dropped
        if common_ratio == 1.0: return 0

        # round up to next power of common_ratio
        rounded_ranks_since_mrca = (
            common_ratio
            ** int(math.ceil(math.log(max_ranks_since_mrca, common_ratio)))
        )
        # should be leq just multiplying max_ranks_since_mrca by common_ratio
        assert (
            rounded_ranks_since_mrca <= max_ranks_since_mrca * common_ratio
            # account for representation error etc.
            or math.isclose(
                rounded_ranks_since_mrca,
                max_ranks_since_mrca * common_ratio,
            )
        )

        # account for increased resolution from interspersal
        return int(math.ceil(rounded_ranks_since_mrca / (interspersal - 1)))

    def CalcRankAtColumnIndex(
        self: 'StratumRetentionPredicateTaperedGeomSeqNthRoot',
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

        num_retained = self.CalcNumStrataRetainedExact(
            num_strata_deposited=num_strata_deposited,
        )
        # allow index equal for in-progress deposition case
        assert 0 <= index <= num_retained

        return next(
            rank for i, rank in enumerate(
                it.chain(
                    self._iter_retained_ranks(num_strata_deposited),
                    # in-progress deposition case
                    (num_strata_deposited,),
                )
            )
            if i == index
        )
