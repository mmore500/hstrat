from iterpop import iterpop as ip
import opytional as opyt
import typing
import warnings

from ..HereditaryStratum import HereditaryStratum
from ..stratum_retention_predicates \
    import StratumRetentionPredicateTaperedGeomSeqNthRoot


class StratumRetentionCondemnerTaperedGeomSeqNthRoot(
    # inherit CalcNumStrataRetainedUpperBound, etc.
    StratumRetentionPredicateTaperedGeomSeqNthRoot,
):
    """TODO

    See Also
    --------
    StratumRetentionPredicateTaperedGeomSeqNthRoot:
        For definitions of methods inherited by this class that describe
        guaranteed properties of the nth root geometric sequence stratum retention
        policy.
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
        self: 'StratumRetentionCondemnerTaperedGeomSeqNthRoot',
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

        super(
            StratumRetentionCondemnerTaperedGeomSeqNthRoot,
            self,
        ).__init__(
            degree=degree,
            interspersal=interspersal,
        )

        self._cached_result = None

    def __call__(
        self: 'StratumRetentionCondemnerTaperedGeomSeqNthRoot',
        num_stratum_depositions_completed: int,
        retained_ranks: typing.Optional[typing.Iterable[int]]=None,
    ) -> typing.Iterator[int]:
        """Decide which strata within the stratagraphic column should be purged.

        Every time a new stratum is deposited, this method is called to
        determine which strata should be purged. All strata at ranks yielded
        from this functor are immediately purged from the column, meaning that
        for a stratum to persist it must not be yielded by this functor each
        and every time a new stratum is deposited.

        Parameters
        ----------
        num_stratum_depositions_completed : int
            The number of strata that have already been deposited, not
            including the latest stratum being deposited which prompted the
            current purge operation.
        retained_ranks : iterator over int, optional
            An iterator over ranks of strata currently retained within the
            hereditary stratigraphic column. Not used in this functor.

        Returns
        -------
        iterator over int
                The ranks of strata that should be purged from the hereditary
            stratigraphic column at this deposition step.

        See Also
        --------
        StratumRetentionPredicateTaperedGeomSeqNthRoot:
            For details on the rationale, implementation, and guarantees of the
            nth root geometric sequence stratum retention policy.
        """

        size_bound = super(
            StratumRetentionCondemnerTaperedGeomSeqNthRoot,
            self,
        ).CalcNumStrataRetainedUpperBound()

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
        elif (
            self._degree
            and opyt.apply_if(
                self._cached_result,
                lambda x: x[0] == num_stratum_depositions_completed - 1,
            )
        ):
            # TODO can this be extended to many more cases (entire logic?)
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
            # note that targets' iterators are drawn from in the order of
            # most ancient to most recent (i.e., k = d down to k = 0)
            #
            # this optimization focuses on the k = 0 iterator, which
            # corresponds to the target that tracks the most recent rank
            # deposited
            #
            # note that this iterator yields reversed(range(n))
            #
            # as n increases, more and more of dropped ranks will correspond
            # to the most ancient rank yielded from the 0th iterator
            #
            # under an ideal scenario where no iterators are exhausted and
            # there is no conflict for the 0th iterator's desired ranks (i.e.,
            # no other iterators have already yielded them), the 0th iterator
            # will yield the last
            #
            # z = size_bound // (degree + 1)
            #
            # ranks (floor division because it is the last to be polled)
            #
            # however, if other iterators are exhausted, the 0th iterator may
            # be polled for more ranks
            #
            # only considering cases where no other iterators are exhausted is
            # a) hard enough to compute to probably negate optimiation benefits
            # b) exclusive against optimization at such timepoints
            #
            # so, let's broaden out and rely on a small amount of caching so
            # that we can account for the fact that the 0th iterator may be
            # providing more than z items to the set of retained ranks even
            # when there is no conflict for the 0th iterator's desired ranks
            #
            # key question:
            # under what conditions is some other rank besides the 0th
            # iterator's most ancient retained rank dropped?
            #
            # key observation:
            # only possible when a new highest-priority rank becomes available
            # to any other iterator
            # (every other iterator gets first dibs above the 0th iterator, so
            # this is the only situation may result in a non-0th iterator's
            # lowest-priority rank getting dropped)
            #
            # so, if there is... [unfinished commentary ends here]
            # ...it turns out that making the 0th root very lowest priority
            # makes this optimization MUCH simpler and more effective...
            # ...so let's refactor but keep this unfinished commentary on the
            # existing approach for posterity
            cached_time, cached_drop = self._cached_result

            # what is the tightest spacing between retained ranks for
            # any non-0th iterator?
            pow1_sep = super(
                StratumRetentionCondemnerTaperedGeomSeqNthRoot,
                self,
            )._calc_rank_sep(
                1,
                cached_drop,
            ) // 2
            if pow1_sep == 0:
                pow1_sep = 1

            # TODO should this be +1?
            pow1_frontstop = (
                (num_stratum_depositions_completed + 1)
                - (num_stratum_depositions_completed + 1) % pow1_sep
            )
            if pow1_frontstop - 1 < cached_drop:
                # if -2 this fails
                res = {
                    cached_drop + 1,
                }

        # fallback to do full computation
        if res is None:
            prev_retained_ranks = super(
                StratumRetentionCondemnerTaperedGeomSeqNthRoot,
                self,
            )._get_retained_ranks(
                num_stratum_depositions_completed,
            )

            cur_retained_ranks = super(
                StratumRetentionCondemnerTaperedGeomSeqNthRoot,
                self,
            )._get_retained_ranks(
                num_stratum_depositions_completed + 1,
            )

            # take set difference between prev retained ranks and cur retained ranks
            res = (prev_retained_ranks - cur_retained_ranks)

        # if res is not empty, it will only have one rank
        # cache that dropped rank with the current timepoint
        if res:
            self._cached_result = (
                num_stratum_depositions_completed,
                ip.popsingleton(res),
            )

        yield from res
