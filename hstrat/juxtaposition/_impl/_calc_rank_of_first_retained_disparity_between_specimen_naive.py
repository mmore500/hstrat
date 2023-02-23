import typing

from interval_search import binary_search
import numpy as np
import opytional as opyt

from ..._auxiliary_lib import (
    iter_monotonic_equivalencies,
    iter_monotonic_equivalencies_reverse,
    jit,
    numpy_index_flat,
    reversed_range,
)
from ...frozen_instrumentation import HereditaryStratigraphicSpecimen
from .._calc_min_implausible_spurious_consecutive_differentia_collisions_between import (
    calc_min_implausible_spurious_consecutive_differentia_collisions_between,
)
from ._calc_rank_of_first_retained_disparity_between_generic import (
    calc_rank_of_first_retained_disparity_between_generic,
)

_reversed_range_jit = jit(nopython=True)(reversed_range)


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


@jit(nopython=True)
def _find_first_disparity_or_last_commonality(
    first_ranks: np.array,
    first_differentiae: np.array,
    second_ranks: np.array,
    second_differentiae: np.array,
) -> typing.Optional[typing.Tuple[int, int]]:
    for positions, comp in _compare_differentia_at_common_ranks(
        first_ranks, first_differentiae, second_ranks, second_differentiae
    ):
        if not comp:
            return positions
    else:
        return positions


@jit(nopython=True)
def _backtrack_n_equivalencies(
    first_ranks: np.array,
    second_ranks: np.array,
    start: typing.Tuple[int, int],
    n: int,
    strict: bool,
) -> typing.Tuple[int, int]:

    for i, positions in enumerate(
        iter_monotonic_equivalencies_reverse(
            first_ranks,
            second_ranks,
            start=start,
        )
    ):
        if i == n:
            return positions
    else:
        if strict:
            return None
        else:
            return (0, 0)


def calc_rank_of_first_retained_disparity_between_specimen_naive(
    first: HereditaryStratigraphicSpecimen,
    second: HereditaryStratigraphicSpecimen,
    confidence_level: float,
) -> typing.Optional[int]:
    """Find first mismatching strata between columns.

    Implementation detail. Searches forward from index 0 for first mismatching
    retained differentiae between columns.
    """

    # terminology
    # rank: generation of deposition
    # loc: index among all strata
    # pos: index among common strata

    assert (
        first.GetStratumDifferentiaBitWidth()
        == second.GetStratumDifferentiaBitWidth()
    )
    diff_bit_width = first.GetStratumDifferentiaBitWidth()

    if diff_bit_width > 64:
        # object-type numpy arrays breaks Numba nopython jit; send elsewhere
        return calc_rank_of_first_retained_disparity_between_generic(
            first, second, confidence_level=confidence_level
        )

    first_vals = first.GetDifferentiaVals()
    second_vals = second.GetDifferentiaVals()
    first_ranks = first.GetRankIndex()
    second_ranks = second.GetRankIndex()

    first_pos, second_pos = _find_first_disparity_or_last_commonality(
        first_ranks, first_vals, second_ranks, second_vals
    )
    assert 0 <= first_pos < first.GetNumStrataRetained()
    assert 0 <= second_pos < second.GetNumStrataRetained()

    collision_plausibility_threshold = (
        calc_min_implausible_spurious_consecutive_differentia_collisions_between(
            first,
            second,
            significance_level=1.0 - confidence_level,
        )
        - 1
    )
    num_backtrack = collision_plausibility_threshold

    if first_vals[first_pos] == second_vals[second_pos]:
        if collision_plausibility_threshold == 0:
            if first.GetNumStrataDeposited() == second.GetNumStrataDeposited():
                return None
            else:
                return min(
                    first.GetNumStrataDeposited(),
                    second.GetNumStrataDeposited(),
                )
        else:
            num_backtrack -= 1

    if num_backtrack:
        assert first_ranks[first_pos] == second_ranks[second_pos]
        first_pos, second_pos = _backtrack_n_equivalencies(
            first_ranks,
            second_ranks,
            start=(first_pos, second_pos),
            n=num_backtrack,
            strict=False,
        )
        assert 0 <= first_pos < first.GetNumStrataRetained()
        assert 0 <= second_pos < second.GetNumStrataRetained()

    assert first_ranks[first_pos] == second_ranks[second_pos]
    return first_ranks[first_pos]
