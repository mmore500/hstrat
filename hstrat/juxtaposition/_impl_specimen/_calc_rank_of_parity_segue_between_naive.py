import typing

import numpy as np

from ..._auxiliary_lib import (
    iter_monotonic_equivalencies_reverse,
    jit,
    reversed_range,
)
from ...frozen_instrumentation import HereditaryStratigraphicSpecimen
from .._calc_min_implausible_spurious_consecutive_differentia_collisions_between import (
    calc_min_implausible_spurious_consecutive_differentia_collisions_between,
)
from .._impl_column._calc_rank_of_parity_segue_between import (
    calc_rank_of_parity_segue_between,
)
from ._iter_mutual_rank_indices import _compare_differentia_at_common_ranks

_reversed_range_jit = jit(nopython=True)(reversed_range)


@jit(nopython=True)
def _find_first_disparity_or_last_commonality(
    first_ranks: np.ndarray,
    first_differentiae: np.ndarray,
    second_ranks: np.ndarray,
    second_differentiae: np.ndarray,
) -> typing.Optional[typing.Tuple[int, int]]:
    for positions, comp in _compare_differentia_at_common_ranks(
        first_ranks, first_differentiae, second_ranks, second_differentiae
    ):
        if not comp:
            return positions
    return positions


@jit(nopython=True)
def _backtrack_n_equivalencies(
    first_ranks: np.ndarray,
    second_ranks: np.ndarray,
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
    if strict:
        return None
    else:
        return (0, 0)


def calc_rank_of_parity_segue_between_naive(
    first: HereditaryStratigraphicSpecimen,
    second: HereditaryStratigraphicSpecimen,
    confidence_level_commonality: float,
    confidence_level_disparity: float,
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
        return calc_rank_of_parity_segue_between(
            first,
            second,
            confidence_level_commonality=confidence_level_commonality,
            confidence_level_disparity=confidence_level_disparity,
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

    def calc_disparity(first_pos, second_pos):
        collision_plausibility_threshold = (
            calc_min_implausible_spurious_consecutive_differentia_collisions_between(
                first,
                second,
                significance_level=1.0 - confidence_level_disparity,
            )
            - 1
        )
        num_backtrack = collision_plausibility_threshold

        if first_vals[first_pos] == second_vals[second_pos]:
            if collision_plausibility_threshold == 0:
                if (
                    first.GetNumStrataDeposited()
                    == second.GetNumStrataDeposited()
                ):
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
        # must convert to Python int; although integral,
        # numpy ints are experiencing unwanted conversion to floats
        assert isinstance(first_ranks[first_pos], np.integer)
        assert int(first_ranks[first_pos]) >= 0
        return int(first_ranks[first_pos])

    def calc_commonality(first_pos, second_pos):
        collision_plausibility_threshold = calc_min_implausible_spurious_consecutive_differentia_collisions_between(
            first,
            second,
            significance_level=1.0 - confidence_level_commonality,
        )
        assert collision_plausibility_threshold > 0
        num_backtrack = collision_plausibility_threshold
        assert num_backtrack > 0

        if first_vals[first_pos] == second_vals[second_pos]:
            num_backtrack -= 1

        assert first_ranks[first_pos] == second_ranks[second_pos]
        # discount collision_implausibility_threshold - 1 common strata
        # as potential spurious differentia collisions
        res = _backtrack_n_equivalencies(
            first_ranks,
            second_ranks,
            start=(first_pos, second_pos),
            n=num_backtrack,
            strict=True,
        )
        if res is None:
            # not enough common strata to discount the possibility all
            # are spurious collisions with respect to the given confidence
            # level; conservatively conclude there is no common ancestor
            return res
        else:
            first_pos, second_pos = res
            assert 0 <= first_pos < first.GetNumStrataRetained()
            assert 0 <= second_pos < second.GetNumStrataRetained()
            assert first_ranks[first_pos] == second_ranks[second_pos]
            # must convert to Python int; although integral,
            # numpy ints are experiencing unwanted conversion to floats
            assert isinstance(first_ranks[first_pos], np.integer)
            assert int(first_ranks[first_pos]) >= 0
            return int(first_ranks[first_pos])

    return (
        calc_commonality(first_pos, second_pos)
        if confidence_level_commonality is not None
        else None,
        calc_disparity(first_pos, second_pos)
        if confidence_level_disparity is not None
        else None,
    )
