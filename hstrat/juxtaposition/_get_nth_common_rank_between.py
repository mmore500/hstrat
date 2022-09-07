import typing

from ..genome_instrumentation import HereditaryStratigraphicColumn


def get_nth_common_rank_between(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    n: int,
) -> typing.Optional[int]:
    """Return the nth rank retained by both columns.

    Zero indexed. Returns None if n + 1 common ranks do not exist between
    first and second.
    """
    assert n >= 0

    # helper setup
    first_iter = first._stratum_ordered_store.IterRankDifferentia(
        get_rank_at_column_index=first.GetRankAtColumnIndex,
    )
    second_iter = second._stratum_ordered_store.IterRankDifferentia(
        get_rank_at_column_index=second.GetRankAtColumnIndex,
    )
    first_cur_rank, first_cur_differentia = next(first_iter)
    second_cur_rank, second_cur_differentia = next(second_iter)

    try:
        while True:
            if first_cur_rank == second_cur_rank:
                # strata at common rank
                if n == 0:
                    return first_cur_rank

                n -= 1
                # advance first
                first_cur_rank, first_cur_differentia = next(first_iter)
                # advance second
                second_cur_rank, second_cur_differentia = next(second_iter)
            elif first_cur_rank < second_cur_rank:
                # current stratum on first column older than on second column
                # advance to next-newer stratum on first column
                first_cur_rank, first_cur_differentia = next(first_iter)
            elif first_cur_rank > second_cur_rank:
                # current stratum on second column older than on first column
                # advance to next-newer stratum on second column
                second_cur_rank, second_cur_differentia = next(second_iter)

    except StopIteration:
        return None
