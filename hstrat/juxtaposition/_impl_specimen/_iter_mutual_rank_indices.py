import typing

import numpy as np

from ..._auxiliary_lib import iter_monotonic_equivalencies, jit
from ...frozen_instrumentation import HereditaryStratigraphicSpecimen


@jit(nopython=True)
def _compare_differentia_at_common_ranks(
    first_ranks: np.array,
    first_differentiae: np.array,
    second_ranks: np.array,
    second_differentiae: np.array,
) -> typing.Iterator[typing.Tuple[typing.Tuple[int, int], bool]]:
    for pos1, pos2 in iter_monotonic_equivalencies(first_ranks, second_ranks):
        yield (
            (pos1, pos2),
            first_differentiae[pos1] == second_differentiae[pos2],
        )


def iter_mutual_rank_indices(
    first: HereditaryStratigraphicSpecimen,
    second: HereditaryStratigraphicSpecimen,
    compare: bool = False,
) -> typing.Union[
    typing.Iterator[typing.Tuple[int, int]],
    typing.Iterator[typing.Tuple[typing.Tuple[int, int], bool]],
]:
    """Iterate over ranks with matching strata between columns in ascending
    order."""
    if compare:
        return _compare_differentia_at_common_ranks(
            first.GetRankIndex(),
            first.GetDifferentiaVals(),
            second.GetRankIndex(),
            second.GetDifferentiaVals(),
        )

    else:
        return iter_monotonic_equivalencies(
            first.GetRankIndex(), second.GetRankIndex()
        )
