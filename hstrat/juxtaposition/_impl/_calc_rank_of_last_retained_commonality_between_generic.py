from collections import deque
import typing

from ...genome_instrumentation import HereditaryStratigraphicColumn


def calc_rank_of_last_retained_commonality_between_generic(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    *,
    first_start_idx: int = 0,
    second_start_idx: int = 0,
    confidence_level: float,
) -> typing.Optional[int]:
    """Find rank of strata commonality before first strata disparity.

    Implementation detail with general-case implementation.
    """
    # helper setup
    first_iter = first._stratum_ordered_store.IterRankDifferentia(
        get_rank_at_column_index=first.GetRankAtColumnIndex,
        start_column_index=first_start_idx,
    )
    second_iter = second._stratum_ordered_store.IterRankDifferentia(
        get_rank_at_column_index=second.GetRankAtColumnIndex,
        start_column_index=second_start_idx,
    )
    first_cur_rank, first_cur_differentia = next(first_iter)
    second_cur_rank, second_cur_differentia = next(second_iter)

    # we need to keep track of enough ranks of last-seen common strata so
    # that we can discount this many (minus 1) as potentially occuring due
    # to spurious differentia collisions
    collision_implausibility_threshold = (
        first.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
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
    #     first_column_idx < first.GetNumStrataRetained()
    #     and second_column_idx < second.GetNumStrataRetained()
    # ):
    try:
        while True:
            if first_cur_rank == second_cur_rank:
                # strata at same rank can be compared
                if first_cur_differentia == second_cur_differentia:
                    # matching differentiae at the same rank,
                    # store rank and keep searching for mismatch
                    preceding_common_strata_ranks.appendleft(first_cur_rank)
                    # advance first
                    first_cur_rank, first_cur_differentia = next(first_iter)
                    # advance second
                    second_cur_rank, second_cur_differentia = next(second_iter)
                else:
                    # mismatching differentiae at the same rank
                    # a.k.a. break
                    raise StopIteration
            elif first_cur_rank < second_cur_rank:
                # current stratum on first column older than on second column
                # advance to next-newer stratum on first column
                first_cur_rank, first_cur_differentia = next(first_iter)
            elif first_cur_rank > second_cur_rank:
                # current stratum on second column older than on first column
                # advance to next-newer stratum on second column
                second_cur_rank, second_cur_differentia = next(second_iter)
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
