import typing

import numpy as np

from ..._auxiliary_lib import (
    iter_monotonic_equivalencies,
    jit,
    jit_numba_uint8_arr_t,
    jit_numba_uint16_arr_t,
    jit_numba_uint32_arr_t,
    jit_numba_uint64_arr_t,
)
from ...frozen_instrumentation import HereditaryStratigraphicSpecimen


@jit(
    [
        (
            jit_numba_uint64_arr_t,
            differentia_array_t,
            jit_numba_uint64_arr_t,
            differentia_array_t,
        )
        for differentia_array_t in (
            jit_numba_uint8_arr_t,
            jit_numba_uint16_arr_t,
            jit_numba_uint32_arr_t,
            jit_numba_uint64_arr_t,
        )
    ],
    nopython=True,
)
def _compare_differentia_at_common_ranks(
    first_ranks: np.ndarray,
    first_differentiae: np.ndarray,
    second_ranks: np.ndarray,
    second_differentiae: np.ndarray,
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
