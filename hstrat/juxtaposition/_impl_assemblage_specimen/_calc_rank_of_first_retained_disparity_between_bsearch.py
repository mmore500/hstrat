import typing

import numpy as np

from ..._auxiliary_lib import curried_binary_search_jit, jit, reversed_range
from ...frozen_instrumentation import HereditaryStratigraphicAssemblageSpecimen
from .._calc_min_implausible_spurious_consecutive_differentia_collisions_between import (
    calc_min_implausible_spurious_consecutive_differentia_collisions_between,
)
from .._impl_column._calc_rank_of_first_retained_disparity_between_generic import (
    calc_rank_of_first_retained_disparity_between_generic,
)

_reversed_range_jit = jit(nopython=True)(reversed_range)


# TODO indexes -> indices


def calc_rank_of_first_retained_disparity_between_bsearch(
    first: HereditaryStratigraphicAssemblageSpecimen,
    second: HereditaryStratigraphicAssemblageSpecimen,
    confidence_level: float,
) -> typing.Optional[int]:
    """Find first mismatching strata between columns.

    Implementation detail. Provides optimized implementation for special
    case where both self and second use the perfect resolution stratum
    retention policy.
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
    first_mask = first.GetStratumMask()
    second_mask = second.GetStratumMask()

    lower_bound_loc = 0
    upper_bound_loc = min(len(first_vals), len(second_vals))  # exclusive
    assert lower_bound_loc <= upper_bound_loc

    common_strata_mask = ~(
        first_mask[lower_bound_loc:upper_bound_loc]
        | second_mask[lower_bound_loc:upper_bound_loc]
    )
    num_common_strata = common_strata_mask.sum()
    common_locs = np.arange(lower_bound_loc, upper_bound_loc)[
        common_strata_mask
    ]

    @jit(nopython=True)
    def is_nonhomologous(pos: int) -> bool:
        num_matches = 0
        for pos_ in _reversed_range_jit(pos + 1):
            loc_ = common_locs[pos_]
            assert not first_mask[loc_]
            assert not second_mask[loc_]

            if first_vals[loc_] == second_vals[loc_]:
                num_matches += diff_bit_width
            else:
                return True

            # use 128 bits as plausibility threshold for optimization
            # https://en.wikipedia.org/wiki/Universally_unique_identifier
            if num_matches >= 128:
                return False
        else:
            return False

        assert False

    lower_bound_pos = lower_bound_loc  # for now
    upper_bound_pos = len(common_locs)  # exclusive
    first_disparite_pos = curried_binary_search_jit(is_nonhomologous)(
        lower_bound_pos, upper_bound_pos - 1
    )

    #     (first_vals != second_vals) & ~first_mask & ~second_mask
    # )
    # first_disparite_loc = numpy_index_flat(
    #     true_disparities,
    #     True,
    #     -1,
    # )
    if first_disparite_pos is None:
        # no disparate strata found
        first_disparite_pos = num_common_strata

    collision_plausibility_threshold = (
        calc_min_implausible_spurious_consecutive_differentia_collisions_between(
            first,
            second,
            significance_level=1.0 - confidence_level,
        )
        - 1
    )

    # discount collision_implausibility_threshold - 1 common
    # ranks due to potential spurious differentia collisions;
    # if not enough common ranks are available we still know
    # *definitively* that a disparity occured (because we
    # observed disparite strata at the same rank); so, make the
    # conservative assumption that the disparity occured as far
    # back as possible (rank 0)
    spurious_collision_corrected_pos = (
        first_disparite_pos - collision_plausibility_threshold
    )
    if spurious_collision_corrected_pos < 0:
        return 0
    elif spurious_collision_corrected_pos == len(common_locs):
        if first.GetNumStrataDeposited() == second.GetNumStrataDeposited():
            # no disparate strata found
            # and first and second have the same newest rank
            # and first and second have the same newest rank
            return None
        else:
            # although no mismatching strata found between first and second
            # a has strata ranks beyond the newest found in b
            # conservatively assume mismatch will be with next rank of b
            return first.GetRankIndex()[common_locs[-1]] + 1
    elif spurious_collision_corrected_pos < len(common_locs):
        first_disparite_loc = common_locs[spurious_collision_corrected_pos]
        return first.GetRankIndex()[first_disparite_loc]
    else:
        assert False
