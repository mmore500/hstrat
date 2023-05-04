import typing

from iterpop import iterpop as ip
import opytional as opyt
from safe_assert import safe_assert as always_assert

from ...._detail import PolicyCouplerBase
from ..._PolicySpec import PolicySpec
from ..._impl import calc_rank_sep, get_retained_ranks


class GenDropRanks:
    """Functor to implement the approximate space-filling MRCA-recency-
    proportional resolution stratum retention policy, for use with
    HereditaryStratigraphicColumn.

    This functor enacts the approximate space-filling MRCA-recency-
    proportional resolution stratum retention policy by specifying the set of
    strata ranks that should be purged from a hereditary stratigraphic column
    when the nth stratum is deposited.
    """

    # store the most recent result from calls to __call__ that dropped a rank
    # in the format
    #
    # (num_stratum_depositions_completed, dropped_rank)
    #
    # this cache enables optimization if calls to __call__ are made in
    # monotonically increasing order with respect to
    # num_stratum_depositions_completed but is not necessary for __call__ to
    # produce a correct result
    # (if the optimization is not available, dropped rank is computed using a
    # slower fallback method)
    #
    # note that because this policy maintains column size exactly at a fixed
    # size bound so at most only one rank will be dropped when a new stratum is
    # deposited
    # (zero ranks are dropped while the column is growing to that size bound)
    _cached_result: typing.Optional[typing.Tuple[int, int]]

    def __init__(
        self: "GenDropRanks",
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        self._cached_result = None

    def __eq__(self: "GenDropRanks", other: typing.Any) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "GenDropRanks",
        policy: PolicyCouplerBase,
        num_stratum_depositions_completed: int,
        retained_ranks: typing.Optional[typing.Iterable[int]],
    ) -> typing.Iterator[int]:
        """Decide which strata within the stratagraphic column should be purged.

        Every time a new stratum is deposited, this method is called to
        determine which strata should be purged. All strata at ranks yielded
        from this functor are immediately purged from the column, meaning that
        for a stratum to persist it must not be yielded by this functor each
        and every time a new stratum is deposited.

        Parameters
        ----------
        policy: Policy
            Policy this functor enacts.
        num_stratum_depositions_completed : int
            The number of strata that have already been deposited, not
            including the latest stratum being deposited which prompted the
            current purge operation.
        retained_ranks : iterator over int
            An iterator over ranks of strata currently retained within the
            hereditary stratigraphic column. Not used in this functor.

        Returns
        -------
        iterator over int
                The ranks of strata that should be purged from the hereditary
            stratigraphic column at this deposition step.

        See Also
        --------
        depth_proportional_resolution_tapered_algo:
            For details on the rationale, implementation, and guarantees of the
            tapered depth-proportional resolution stratum retention policy.
        """
        spec = policy.GetSpec()

        size_bound = policy.CalcNumStrataRetainedUpperBound(
            num_stratum_depositions_completed,
        )

        # try a series of shortcuts that only apply in certain cases
        # if no shortcut cases are available (and res is still None), fallback
        # to calculating res as the difference between cur retained ranks and
        # prev retained ranks
        res = None

        # if we haven't filled up available space, no ranks are dropped
        if num_stratum_depositions_completed < size_bound:
            res = set()
        # if we have a cached result for the current time point, use it
        elif opyt.apply_if(
            self._cached_result,
            lambda x: x[0] == num_stratum_depositions_completed,
        ):
            cached_time, cached_drop = self._cached_result
            res = {
                cached_drop,
            }
        # if degree > 0 and we have a cached result for the preceding time point
        # try to use shortcut to return same result for current time point
        elif spec.GetDegree() and opyt.apply_if(
            self._cached_result,
            lambda x: x[0] == num_stratum_depositions_completed - 1,
        ):
            # shortcut explanation...
            #
            # recall that the geom seq nth root policy is defined by a fixed
            # degree d and providing guaranteed coverage to d + 1 targets
            #
            # let k range from 0 to d, inclusive and n represent the number of
            # stratum depositions elapsed... then each target tracks rank
            #
            # n - (n)^(k/d)
            #
            # the tapered geom seq nth root policy extends the above by
            # retaining additional ranks to ensure that a fixed size is
            # maintained
            #
            # the tapered geom seq nth root policy accomplishes this by
            # creating an iterator over priority ranks for each kth target and
            # drawing round robin from these iterators
            #
            # each iterator is drawn from until a novel (not yet decided for
            # retention) rank is yielded, then the next iterator is drawn from
            #
            # if an iterator is exhausted, it is skipped over (so the set of
            # remaining iterators will be polled an additional rank than they
            # would not have had to produce otherwise)
            #
            # note that the pool of retained ranks being drawn into is seeded
            # with rank 0 and rank n - 1, because these must be retained
            #
            # note also that targets' iterators are drawn from in the order of
            # most ancient to most recent (i.e., k = d down to k = 1)
            #
            # in order to make this shortcut optimization more effective and
            # simplify its implementation, the k = 0 iterator is excluded from
            # this phase
            #
            # only after (and if) all k > 0 iterators have been exhausted is
            # the k = 0 iterator drawn from
            #
            # the k = 0 iterator is the lowest-priority iterator that
            # exclusively vacuums up (i.e., yields) ranks that have been
            # yielded from no other iterator... put another way, the k = 0
            # iterator will never pre-empt another iterator by claiming a rank
            # "first"
            #
            #
            # this optimization focuses on the k = 0 iterator, which
            # corresponds to the target that tracks the most recent rank
            # deposited
            #
            # because the k = 0 target tracks the most recent rank, the k = 0
            # iterator yields all deposited ranks in reverse order
            # i.e., this iterator yields reversed(range(n))
            #
            # as n increases, more and more of dropped ranks will correspond
            # to the most ancient rank yielded from the 0th iterator
            # (considering the implicit seed n - 1 as yielded from this
            # iterator)
            #
            # under an ideal scenario where no iterators are exhausted the 0th
            # iterator will yield just the second-to-last rank (i.e., n - 2)
            # because the last rank is always retained
            #
            # however, if other iterators are exhausted, the 0th iterator may
            # be polled for more ranks
            #
            # only considering cases where no other iterators are exhausted
            # a) is hard enough computationally to probably negate opt benefits
            # b) reduces the cases where this optimization applies (i.e.,
            #    excludes optimization at such timepoints)
            #
            # that raises the question, how to compute the number of items
            # yielded from the k = 0 iterator?
            #
            # we will employ a small amount of caching to sidestep this
            # problem: we can look at the number of items yielded from the
            # k = 0 iterator at the previous timepoint
            #
            # our shortcut optimization will rely on detecting whether
            # 1) there could possibly have been any change to the number of
            #    items yielded from the k = 0 iterator due to a new highest-
            #    priority rank becoming available to any other k > 1 iterator
            #    (which would cause the to dropped rank jump forward more than
            #    one position) (every other iterator gets first dibs above the
            #    k = 0 iterator, so this is the only situation may result in a
            #    k > 0 iterator's lowest-priority rank getting dropped)
            # 2) there could possibly be a latent rank being retained by a
            #    k > 0 iterator at the end of the chain of k = 0's retain ranks
            #    that the k = 0 iterator's retained rainks had previously been
            #    stepping over (thereby extending the k = 0 iterator's most
            #    ancient retained rank backward) (and might cause the dropped
            #    rank to jump forward more than one position)
            #
            # if neither of these scenarios is possible, we can guarantee that
            # the next dropped rank will immediately succeed the previous
            # (cached) dropped rank
            #
            # scenario 1 is only possible when the deposited rank could align
            # with the current sep (rank-to-rank step size) of the k = 1
            # iterator
            # (all iterators k > 1 have monotonically increasing seps that only
            # increase by doubling so are covered by checking the k = 1 case)
            #
            # scenario 2 is only possible when the rank-to-be-dropped could
            # have been retained as a priority rank of a k > 1 iterator...
            # so, check whether the contemporaneous to rank-to-be-dropped k = 1
            # sep could have aligned with that rank
            # (again, all iterators k > 1 have monotonically increasing seps
            # that only increase by doubling so are covered by checking the
            # k = 1 case)
            #
            # NOTE: on further reflection, it seems that scenario 2 is the only
            # relevant scenario because the newly-added rank is always
            # guaranteed to be retained due to the pool of retained ranks being
            # seeded with it... have disabled unnecessary restriction below

            # unpack cache
            cached_time, cached_drop_rank = self._cached_result
            assert cached_drop_rank > 0

            # what is the tightest spacing between retained ranks for
            # any non-0th pow iterator at the current timepoint?
            # allows us to detect whether deposited rank is relevant to any
            # k > 1 iterator
            pow1_newsep = calc_rank_sep(
                spec.GetDegree(),
                spec.GetInterspersal(),
                1,
                # no +1 to be conservative
                num_stratum_depositions_completed,
            )
            # what is the tightest spacing between retained ranks for
            # any non-0th pow iterator at the end of the k = 0 retention chain?
            # (i.e., at rank-to-be-dropped)
            # allows us to detect any possible ranks retained for k > 0
            # that may be retained even if the apparent k = 0 retention chain
            # advances past them
            # (this would interfere with our assumption of the k = 0 drop
            # moving forward one rank per deposition)
            pow1_oldsep = calc_rank_sep(
                spec.GetDegree(),
                spec.GetInterspersal(),
                1,
                # no +1 to be conservative
                cached_drop_rank,
            )
            assert pow1_oldsep <= pow1_newsep

            if (
                # scenario 1 (NOT ACTUALLY NECESSARY, DISABLED)
                # ensure deposited rank is irrelevant to all pow > 0
                # no +1 due to translation from len to index of last
                #
                # num_stratum_depositions_completed % pow1_newsep > 1 and
                #
                # scenario 2
                # ensure rank-to-drop isn't possibly retained for pow > 0
                (cached_drop_rank + 1) % pow1_oldsep
                > 1
                # ^^^ note that >1's ensure that we are at least two ranks
                # past any problem rank (i.e., that the preceding call
                # computed a drop_rank at the end of the k = 0 retention chain)
            ):
                # sufficient guarantee drop moves forward exactly 1
                res = {
                    # drop rank 1 past the one we last dropped
                    cached_drop_rank
                    + 1,
                }

        elif spec.GetDegree():
            # TODO case with no caching?
            # can we prove when pow0 retention chain is only 1 long?
            # i.e., previous iterators don't exhaust?
            pass

        prev_retained_ranks = get_retained_ranks(
            policy,
            num_stratum_depositions_completed,
        )

        cur_retained_ranks = get_retained_ranks(
            policy,
            num_stratum_depositions_completed + 1,
        )

        if res is not None:
            always_assert(
                res == (prev_retained_ranks - cur_retained_ranks),
                {
                    "res": res,
                    "(prev_retained_ranks - cur_retained_ranks)": (
                        prev_retained_ranks - cur_retained_ranks
                    ),
                },
            )
        else:
            res = prev_retained_ranks - cur_retained_ranks

        # # have we determined res using a shortcut method?
        # # if not, fall back to do full computation for res
        # if res is None:
        #     prev_retained_ranks = super(
        #         StratumRetentionCondemnerTaperedGeomSeqNthRoot,
        #         self,
        #     )._get_retained_ranks(
        #         num_stratum_depositions_completed,
        #     )
        #
        #     cur_retained_ranks = super(
        #         StratumRetentionCondemnerTaperedGeomSeqNthRoot,
        #         self,
        #     )._get_retained_ranks(
        #         num_stratum_depositions_completed + 1,
        #     )
        #     # take set difference between prev retained ranks and cur retained
        #     # ranks
        #     res = (prev_retained_ranks - cur_retained_ranks)

        # if res is not empty, it will only have one rank
        # cache that dropped rank with the current timepoint
        if res:
            self._cached_result = (
                num_stratum_depositions_completed,
                ip.popsingleton(res),
            )

        yield from res
