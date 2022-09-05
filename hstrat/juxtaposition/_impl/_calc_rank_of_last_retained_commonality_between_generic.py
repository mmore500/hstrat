import typing

from ...genome_instrumentation import HereditaryStratigraphicColumn


def calc_rank_of_last_retained_commonality_between_generic(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    *,
    self_start_idx: int = 0,
    other_start_idx: int = 0,
    confidence_level: float,
) -> typing.Optional[int]:
    """Find rank of strata commonality before first strata disparity.

    Implementation detail with general-case implementation.
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

    # we need to keep track of enough ranks of last-seen common strata so
    # that we can discount this many (minus 1) as potentially occuring due
    # to spurious differentia collisions
    collision_implausibility_threshold = (
        self.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - confidence_level,
        )
    )
    assert collision_implausibility_threshold > 0
    # holds up to n last-seen ranks with common strata,
    # with the newest last-seen rank at the front (index 0)
    # and the up to nth last-seen rank at the back (index -1)
    preceding_common_strata_ranks = deque(
        [], collision_implausibility_threshold
    )
    # a.k.a.
    # while (
    #     self_column_idx < self.GetNumStrataRetained()
    #     and other_column_idx < other.GetNumStrataRetained()
    # ):
    try:
        while True:
            if self_cur_rank == other_cur_rank:
                # strata at same rank can be compared
                if self_cur_differentia == other_cur_differentia:
                    # matching differentiae at the same rank,
                    # store rank and keep searching for mismatch
                    preceding_common_strata_ranks.appendleft(self_cur_rank)
                    # advance self
                    self_cur_rank, self_cur_differentia = next(self_iter)
                    # advance other
                    other_cur_rank, other_cur_differentia = next(other_iter)
                else:
                    # mismatching differentiae at the same rank
                    # a.k.a. break
                    raise StopIteration
            elif self_cur_rank < other_cur_rank:
                # current stratum on self column older than on other column
                # advance to next-newer stratum on self column
                self_cur_rank, self_cur_differentia = next(self_iter)
            elif self_cur_rank > other_cur_rank:
                # current stratum on other column older than on self column
                # advance to next-newer stratum on other column
                other_cur_rank, other_cur_differentia = next(other_iter)
    except StopIteration:
        try:
            # discount collision_implausibility_threshold - 1 common strata
            # as potential spurious differentia collisions
            return preceding_common_strata_ranks[
                collision_implausibility_threshold - 1
            ]
        except IndexError:
            # not enough common strata to discount the possibility all
            # are spurious collisions with respect to the given confidence
            # level; conservatively conclude there is no common ancestor
            return None
