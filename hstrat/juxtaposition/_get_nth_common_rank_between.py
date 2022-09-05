import typing

from ..genome_instrumentation import HereditaryStratigraphicColumn


def get_nth_common_rank_between(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    n: int,
) -> typing.Optional[int]:
    """Return the nth rank retained by both columns.

    Zero indexed. Returns None if n + 1 common ranks do not exist between
    self and other.
    """
    assert n >= 0

    # helper setup
    self_iter = self._stratum_ordered_store.IterRankDifferentia(
        get_rank_at_column_index=self.GetRankAtColumnIndex,
    )
    other_iter = other._stratum_ordered_store.IterRankDifferentia(
        get_rank_at_column_index=other.GetRankAtColumnIndex,
    )
    self_cur_rank, self_cur_differentia = next(self_iter)
    other_cur_rank, other_cur_differentia = next(other_iter)

    try:
        while True:
            if self_cur_rank == other_cur_rank:
                # strata at common rank
                if n == 0:
                    return self_cur_rank

                n -= 1
                # advance self
                self_cur_rank, self_cur_differentia = next(self_iter)
                # advance other
                other_cur_rank, other_cur_differentia = next(other_iter)
            elif self_cur_rank < other_cur_rank:
                # current stratum on self column older than on other column
                # advance to next-newer stratum on self column
                self_cur_rank, self_cur_differentia = next(self_iter)
            elif self_cur_rank > other_cur_rank:
                # current stratum on other column older than on self column
                # advance to next-newer stratum on other column
                other_cur_rank, other_cur_differentia = next(other_iter)

    except StopIteration:
        return None
