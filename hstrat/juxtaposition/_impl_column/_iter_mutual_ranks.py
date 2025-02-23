import typing

from ..._auxiliary_lib import HereditaryStratigraphicArtifact


@typing.overload
def iter_mutual_ranks(
    first: HereditaryStratigraphicArtifact,
    second: HereditaryStratigraphicArtifact,
    *,
    first_start_idx: int = 0,
    second_start_idx: int = 0,
) -> typing.Iterator[int]: ...


@typing.overload
def iter_mutual_ranks(
    first: HereditaryStratigraphicArtifact,
    second: HereditaryStratigraphicArtifact,
    compare: typing.Literal[False],
    *,
    first_start_idx: int = 0,
    second_start_idx: int = 0,
) -> typing.Iterator[int]: ...


@typing.overload
def iter_mutual_ranks(
    first: HereditaryStratigraphicArtifact,
    second: HereditaryStratigraphicArtifact,
    compare: typing.Literal[True],
    *,
    first_start_idx: int = 0,
    second_start_idx: int = 0,
) -> typing.Iterator[typing.Tuple[int, bool]]: ...


@typing.overload
def iter_mutual_ranks(
    first: HereditaryStratigraphicArtifact,
    second: HereditaryStratigraphicArtifact,
    compare: bool = False,
    *,
    first_start_idx: int = 0,
    second_start_idx: int = 0,
) -> typing.Iterator[typing.Union[typing.Tuple[int, bool], int]]: ...


def iter_mutual_ranks(
    first: HereditaryStratigraphicArtifact,
    second: HereditaryStratigraphicArtifact,
    compare: bool = False,
    *,
    first_start_idx: int = 0,
    second_start_idx: int = 0,
) -> typing.Iterator[typing.Union[typing.Tuple[int, bool], int]]:
    """Iterate over ranks with matching strata between columns in ascending
    order."""
    first_iter = zip(
        first.IterRetainedRanks(), first.IterRetainedDifferentia()
    )
    second_iter = zip(
        second.IterRetainedRanks(), second.IterRetainedDifferentia()
    )
    first_cur_rank, first_cur_differentia = next(first_iter)
    second_cur_rank, second_cur_differentia = next(second_iter)

    first_start_rank = first.GetRankAtColumnIndex(first_start_idx)
    second_start_rank = second.GetRankAtColumnIndex(second_start_idx)

    while first_cur_rank < first_start_rank:
        first_cur_rank, first_cur_differentia = next(first_iter)
    while second_cur_rank < second_start_rank:
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
                        (
                            first_cur_rank,
                            False,
                        )
                        if compare
                        else first_cur_rank
                    )
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
