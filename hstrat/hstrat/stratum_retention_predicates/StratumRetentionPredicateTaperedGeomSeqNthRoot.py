import itertools as it
import math
import numpy as np
import typing

from ...helpers import bit_floor, is_nondecreasing


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

        # base ** degree == num_strata_deposited
        # take the degree'th root of each side...
        return num_strata_deposited ** (1 / self._degree)

    def _iter_target_recencies(
        self: 'StratumRetentionPredicateTaperedGeomSeqNthRoot',
        num_strata_deposited: int,
    ):
        """TODO."""

        # target recencies are a geometric sequence
        common_ratio = self._calc_common_ratio(num_strata_deposited)
        for pow in range(self._degree + 1):
            yield common_ratio ** pow

    def _iter_target_ranks(
        self: 'StratumRetentionPredicateTaperedGeomSeqNthRoot',
        num_strata_deposited: int,
    ):
        """TODO."""
        for target_recency in self._iter_target_recencies(num_strata_deposited):
            recency_cutoff = target_recency
            rank_cutoff = max(
                num_strata_deposited - int(math.ceil(recency_cutoff)),
                0,
            )
            if num_strata_deposited == 0: assert rank_cutoff == 0
            else: assert 0 <= rank_cutoff <= num_strata_deposited - 1
            yield rank_cutoff

    def _iter_rank_cutoffs(
        self: 'StratumRetentionPredicateTaperedGeomSeqNthRoot',
        num_strata_deposited: int,
    ):
        """TODO."""
        for target_recency in self._iter_target_recencies(num_strata_deposited):
            rank_cutoff = max(
                num_strata_deposited - int(math.ceil(
                    target_recency
                    * (self._interspersal + 1) / self._interspersal
                )),
                0,
            )
            if num_strata_deposited == 0: assert rank_cutoff == 0
            else: assert 0 <= rank_cutoff <= num_strata_deposited - 1
            yield rank_cutoff

    def _iter_rank_seps(
        self: 'StratumRetentionPredicateTaperedGeomSeqNthRoot',
        num_strata_deposited: int,
    ):
        """TODO."""
        for target_recency in self._iter_target_recencies(num_strata_deposited):
            # spacing between retained ranks
            target_retained_ranks_sep = max(
                target_recency / self._interspersal,
                1.0,
            )
            # round down to power of 2
            retained_ranks_sep = bit_floor(int(target_retained_ranks_sep))
            yield retained_ranks_sep

    def _iter_rank_backstops(
        self: 'StratumRetentionPredicateTaperedGeomSeqNthRoot',
        num_strata_deposited: int,
    ):
        """TODO."""

        for rank_cutoff, retained_ranks_sep in zip(
            self._iter_rank_cutoffs(num_strata_deposited),
            self._iter_rank_seps(num_strata_deposited),
        ):

            # round UP from rank_cutoff
            # adapted from https://stackoverflow.com/a/14092788
            min_retained_rank = (
                rank_cutoff
                - (rank_cutoff % -retained_ranks_sep)
            )
            assert min_retained_rank % retained_ranks_sep == 0

            if num_strata_deposited == 0: assert min_retained_rank == 0
            else: assert 0 <= min_retained_rank <= num_strata_deposited - 1

            yield min_retained_rank

    def _get_nth_pow_retained_ranks(
        self: 'StratumRetentionPredicateTaperedGeomSeqNthRoot',
        n: int,
        num_strata_deposited: int,
    ):
        min_retained_rank = list(
            self._iter_rank_backstops(num_strata_deposited),
        )[n]
        retained_ranks_sep = list(
            self._iter_rank_seps(num_strata_deposited),
        )[n]

        target_ranks = range(
            min_retained_rank, # start
            num_strata_deposited, # stop
            retained_ranks_sep, # sep
        )
        return target_ranks


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

        for target_rank, rank_backstop, retained_ranks_sep, idx in zip(
            self._iter_target_ranks(num_strata_deposited),
            self._iter_rank_backstops(num_strata_deposited),
            self._iter_rank_seps(num_strata_deposited),
            it.count(),
        ):

            min_retained_rank = rank_backstop

            target_ranks = set(range(
                min_retained_rank, # start
                num_strata_deposited, # stop
                retained_ranks_sep, # sep
            ))

            if idx == 0:
                res.update(target_ranks)
                continue

            def has_remaining_capacity():
                return 2 * (interspersal + 1) > len(target_ranks)

            cur_rank = num_strata_deposited
            # cur_sep = retained_ranks_sep
            cur_sep = 1

            while (
                cur_sep
                and cur_rank > cur_sep
                and has_remaining_capacity()
            ):
                cur_rank -= cur_sep
                for rank in reversed(
                    self._get_nth_pow_retained_ranks(idx, cur_rank)
                ):
                    target_ranks.add(rank)
                    if not has_remaining_capacity(): break

            if cur_sep and cur_rank > cur_sep:
                assert not has_remaining_capacity()
            res.update(target_ranks)


            # TODO make this more efficient!
            # miscellaneous ideas
            # must pick these up in the reverse order they were dropped

            # calculate rank of last sep change
            # common_ratio = num_strata_deposited ** (1 / self._degree)
            # target_recency = common_ratio ** idx
            # target_retained_ranks_sep = max(
            #     target_recency / self._interspersal,
            #     1.0,
            # )
            # # round down to power of 2
            # retained_ranks_sep = bit_floor(int(target_retained_ranks_sep))

            # target_recency = num_strata_deposited ** (idx / self._degree)
            # target_retained_ranks_sep = max(
            #     target_recency / self._interspersal,
            #     1.0,
            # )
            # # round down to power of 2
            # retained_ranks_sep = bit_floor(int(target_retained_ranks_sep))

            # cur_ranks_sep
            #   = num_strata_deposited ** (idx / self._degree)
            #         / self._interspersal

            # retained_ranks_sep * self._interspersal
            #   = num_strata_deposited ** (idx / self._degree)

            # (retained_ranks_sep * self._interspersal) ** (self._degree / idx)
            # = num_strata_deposited

            # num_strata_deposited =
            # (cur_ranks_sep * self._interspersal) ** (self._degree / idx)

            # or if idx == 0
            # cur_ranks_sep
            #   = 1 / self._interspersal

            #ignore idx == 0 for now

            # last_doubling_rank = (cur_sep * interspersal) ** (self._degree / idx)


            # while (
            #     interspersal > 1
            #     and remaining_capacity
            #     and cur_sep #// 2
            #     and cur_rank > cur_sep
            # ):
            #     remaining_capacity -= 1
            #     # cur_sep = max([*self._iter_rank_seps(
            #     #     cur_rank #- cur_sep #// 2
            #     # )][idx],1)
            #     cur_rank -= cur_sep
            #     target_ranks.add(cur_rank)
            #
            #
            # target_ranks.update(set(range(
            #     min_retained_rank,
            #     0,
            #     -retained_ranks_sep, # sep
            # )[:remaining_capacity]))
            #
            # if remaining_capacity and retained_ranks_sep // 2:
            #     candidate_ranks = range(
            #         min_retained_rank + retained_ranks_sep // 2, # start
            #         num_strata_deposited, # stop
            #         retained_ranks_sep, # sep
            #     )
            #     target_ranks.update(
            #         # last up to remaining_capacity elements of range
            #         # candidate_ranks[-interspersal:],
            #         # candidate_ranks[:remaining_capacity],
            #         candidate_ranks[:remaining_capacity],
            #     )
            #     # retained_ranks_sep //= 2

            # res.update(target_ranks)

        assert all(isinstance(n, int) for n in res)
        assert all(0 <= n < num_strata_deposited for n in res)
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

        return len(self._get_retained_ranks(num_strata_deposited))

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
        num_strata_deposited: int,
    ):
        """At most, how many strata are retained after n deposted? Inclusive."""

        # +2 is 0th rank and last rank
        return self._degree * 2 * (self._interspersal + 1) + 1

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
        assert rounded_ranks_since_mrca <= max_ranks_since_mrca * common_ratio

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
