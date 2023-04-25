import typing

from ...genome_instrumentation import HereditaryStratigraphicColumn


def iter_mutual_ranks(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    compare: bool = False,
    *,
    first_start_idx: int = 0,
    second_start_idx: int = 0,
) -> typing.Union[typing.Iterator[int], typing.Tuple[int, bool]]:
    """Iterate over ranks with matching strata between columns in ascending
    order."""
    # helper setup
    try:
        first_iter = first._stratum_ordered_store.IterRankDifferentiaZip(
            get_rank_at_column_index=first.GetRankAtColumnIndex,
            start_column_index=first_start_idx,
        )
        second_iter = second._stratum_ordered_store.IterRankDifferentiaZip(
            get_rank_at_column_index=second.GetRankAtColumnIndex,
            start_column_index=second_start_idx,
        )
    except AttributeError:
        first_iter = zip(
            first.IterRetainedRanks(), first.IterRetainedDifferentia()
        )
        second_iter = zip(
            second.IterRetainedRanks(), second.IterRetainedDifferentia()
        )
    first_cur_rank, first_cur_differentia = next(first_iter)
    second_cur_rank, second_cur_differentia = next(second_iter)

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
                    yield (first_cur_rank, True) if compare else first_cur_rank
                    # advance first
                    first_cur_rank, first_cur_differentia = next(first_iter)
                    # advance second
                    second_cur_rank, second_cur_differentia = next(second_iter)
                else:
                    # mismatching differentiae at the same rank
                    yield (
                        first_cur_rank,
                        False,
                    ) if compare else first_cur_rank
            elif first_cur_rank < second_cur_rank:
                # current stratum on first column older than on second column
                # advance to next-newer stratum on first column
                first_cur_rank, first_cur_differentia = next(first_iter)
            elif first_cur_rank > second_cur_rank:
                # current stratum on second column older than on first column
                # advance to next-newer stratum on second column
                second_cur_rank, second_cur_differentia = next(second_iter)
    except StopIteration:
        return
