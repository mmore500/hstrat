import typing

from ..._auxiliary_lib import jit, numpy_index_flat, reversed_range
from ...frozen_instrumentation import HereditaryStratigraphicAssemblageSpecimen
from .._calc_min_implausible_spurious_consecutive_differentia_collisions_between import (
    calc_min_implausible_spurious_consecutive_differentia_collisions_between,
)
from .._impl_column._calc_rank_of_first_retained_disparity_between_generic import (
    calc_rank_of_first_retained_disparity_between_generic,
)

_reversed_range_jit = jit(nopython=True)(reversed_range)


def calc_rank_of_first_retained_disparity_between_naive(
    first: HereditaryStratigraphicAssemblageSpecimen,
    second: HereditaryStratigraphicAssemblageSpecimen,
    confidence_level: float,
) -> typing.Optional[int]:
    """Find first mismatching strata between columns.

    Implementation detail. Searches forward from index 0 for first mismatching
    retained differentiae between columns
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

    common_strata_mask = ~(first_mask | second_mask)
    true_disparities = common_strata_mask & (first_vals != second_vals)

    upper_bound_loc = (
        numpy_index_flat(common_strata_mask, True, -1) + 1
    )  #  exclusive
    first_disparite_loc = numpy_index_flat(true_disparities, True)

    collision_plausibility_threshold = (
        calc_min_implausible_spurious_consecutive_differentia_collisions_between(
            first,
            second,
            significance_level=1.0 - confidence_level,
        )
        - 1
    )
    if first_disparite_loc is None:
        # no disparate strata found
        first_disparite_loc = upper_bound_loc
        assert all(
            first_vals[common_strata_mask] == second_vals[common_strata_mask]
        )
    else:
        assert first_disparite_loc < upper_bound_loc

    assert not first_disparite_loc > upper_bound_loc
    # discount collision_implausibility_threshold - 1 common
    # ranks due to potential spurious differentia collisions;
    # if not enough common ranks are available we still know
    # *definitively* that a disparity occured (because we
    # observed disparite strata at the same rank); so, make the
    # conservative assumption that the disparity occured as far
    # back as possible (rank 0)
    spurious_collision_corrected_loc = (
        numpy_index_flat(
            common_strata_mask[
                : first_disparite_loc
                + bool(first_disparite_loc < upper_bound_loc)
            ],
            True,
            -collision_plausibility_threshold
            - bool(first_disparite_loc < upper_bound_loc),
        )
        if collision_plausibility_threshold
        else first_disparite_loc
    )

    if spurious_collision_corrected_loc is None:
        return 0
    elif spurious_collision_corrected_loc == upper_bound_loc:
        assert all(
            first_vals[common_strata_mask] == second_vals[common_strata_mask]
        )
        if first.GetNumStrataDeposited() == second.GetNumStrataDeposited():
            # no disparate strata found
            # and first and second have the same newest rank
            # and first and second have the same newest rank
            return None
        else:
            # although no mismatching strata found between first and second
            # a has strata ranks beyond the newest found in b
            # conservatively assume mismatch will be with next rank of b
            return min(
                first.GetNumStrataDeposited(), second.GetNumStrataDeposited()
            )
    elif spurious_collision_corrected_loc < upper_bound_loc:
        return first.GetRankIndex()[spurious_collision_corrected_loc]
    else:
        assert False
