import typing

from ...genome_instrumentation import HereditaryStratigraphicColumn


def calc_rank_of_first_retained_disparity_between_generic(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    *,
    self_start_idx: int = 0,
    other_start_idx: int = 0,
    confidence_level: float,
) -> typing.Optional[int]:
    """Find first mismatching strata between columns.

    Implementation detail. Provides general-case implementation.
    """
    # helper setup
    self_iter = self._stratum_ordered_store.IterRankDifferentia(
        get_rank_at_column_index=self.GetRankAtColumnIndex,
        start_column_index=self_start_idx,
    )
    other_iter = other._stratum_ordered_store.IterRankDifferentia(
        get_rank_at_column_index=other.GetRankAtColumnIndex,
        start_column_index=other_start_idx,
    )
    self_cur_rank, self_cur_differentia = next(self_iter)
    other_cur_rank, other_cur_differentia = next(other_iter)
    self_prev_rank: int
    other_prev_rank: int

    def advance_self():
        nonlocal self_prev_rank, self_cur_rank, self_cur_differentia, self_iter
        try:
            self_prev_rank = self_cur_rank
            self_cur_rank, self_cur_differentia = next(self_iter)
        except StopIteration:
            self_iter = None

    def advance_other():
        nonlocal other_prev_rank, other_cur_rank, other_cur_differentia, other_iter
        try:
            other_prev_rank = other_cur_rank
            other_cur_rank, other_cur_differentia = next(other_iter)
        except StopIteration:
            other_iter = None

    # we need to keep track of enough last-seen common ranks so that we
    # can discount this many (minus 1) as potentially occuring due to
    # spurious differentia collisions
    collision_implausibility_threshold = (
        self.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - confidence_level,
        )
    )
    assert collision_implausibility_threshold > 0
    # holds up to n last-seen common ranks,
    # with the newest last-seen rank at the front (index 0)
    # and the up to nth last-seen rank at the back (index -1)
    preceding_common_ranks = deque([], collision_implausibility_threshold)
    # a.k.a.
    # while (
    #     self_column_idx < self.GetNumStrataRetained()
    #     and other_column_idx < other.GetNumStrataRetained()
    # ):
    while self_iter is not None and other_iter is not None:
        if self_cur_rank == other_cur_rank:
            # strata at same rank can be compared
            if self_cur_differentia == other_cur_differentia:
                preceding_common_ranks.appendleft(self_cur_rank)
                # matching differentiae at the same rank,
                # keep searching for mismatch
                # advance self and other
                # must ensure both advance, even if one stops iteration
                advance_self()
                advance_other()
            else:
                # mismatching differentiae at the same rank
                preceding_common_ranks.appendleft(self_cur_rank)
                assert 0 <= self_cur_rank < self.GetNumStrataDeposited()

                # discount collision_implausibility_threshold - 1 common
                # ranks due to potential spurious differentia collisions;
                # if not enough common ranks are available we still know
                # *definitively* that a disparity occured (because we
                # observed disparite strata at the same rank); so, make the
                # conservative assumption that the disparity occured as far
                # back as possible (the oldest up to nth last-seen common
                # rank, at the back of the deque)
                return preceding_common_ranks[-1]
        elif self_cur_rank < other_cur_rank:
            # current stratum on self column older than on other column
            # advance to next-newer stratum on self column
            advance_self()
        elif self_cur_rank > other_cur_rank:
            # current stratum on other column older than on self column
            # advance to next-newer stratum on other column
            advance_other()

    if self_iter is not None:
        # although no mismatching strata found between self and other
        # self has strata ranks beyond the newest found in other
        # conservatively assume mismatch will be with next rank of other
        assert other_iter is None
        preceding_common_ranks.appendleft(other_prev_rank + 1)
        res = preceding_common_ranks[-1]
        assert 0 <= res <= self.GetNumStrataDeposited()
        assert 0 <= res <= other.GetNumStrataDeposited()
        return res
    elif other_iter is not None:
        # although no mismatching strata found between other and self
        # other has strata ranks beyond the newest found in self
        # conservatively assume mismatch will be with next rank
        assert self_iter is None
        preceding_common_ranks.appendleft(self_prev_rank + 1)
        res = preceding_common_ranks[-1]
        assert 0 <= res <= self.GetNumStrataDeposited()
        assert 0 <= res <= other.GetNumStrataDeposited()
        return res
    else:
        # no disparate strata found
        # and self and other have the same newest rank
        assert self_iter is None and other_iter is None
        preceding_common_ranks.appendleft(None)
        return preceding_common_ranks[-1]
