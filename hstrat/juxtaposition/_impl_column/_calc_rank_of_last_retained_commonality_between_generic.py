from collections import deque
import typing

from ...genome_instrumentation import HereditaryStratigraphicColumn
from .._calc_min_implausible_spurious_consecutive_differentia_collisions_between import (
    calc_min_implausible_spurious_consecutive_differentia_collisions_between,
)
from ._iter_ranks_of_retained_commonality_between import (
    iter_ranks_of_retained_commonality_between,
)


def calc_rank_of_last_retained_commonality_between_generic(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    *,
    first_start_idx: int = 0,
    second_start_idx: int = 0,
    confidence_level: float,
) -> typing.Optional[int]:
    """Find rank of strata commonality before first strata disparity.

    Implementation detail with general-case implementation.
    """
    # we need to keep track of enough ranks of last-seen common strata so
    # that we can discount this many (minus 1) as potentially occuring due
    # to spurious differentia collisions
    assert (
        first.GetStratumDifferentiaBitWidth()
        == second.GetStratumDifferentiaBitWidth()
    )
    collision_implausibility_threshold = calc_min_implausible_spurious_consecutive_differentia_collisions_between(
        first, second, significance_level=1.0 - confidence_level
    )
    assert collision_implausibility_threshold > 0
    # holds up to n last-seen ranks with common strata,
    # with the newest last-seen rank at the front (index 0)
    # and the up to nth last-seen rank at the back (index -1)
    preceding_common_strata_ranks = deque(
        iter_ranks_of_retained_commonality_between(
            first,
            second,
            first_start_idx=first_start_idx,
            second_start_idx=second_start_idx,
        ),
        collision_implausibility_threshold,
    )
    if len(preceding_common_strata_ranks) < collision_implausibility_threshold:
        # not enough common strata to discount the possibility all
        # are spurious collisions with respect to the given confidence
        # level; conservatively conclude there is no common ancestor
        return None
    else:
        # discount collision_implausibility_threshold - 1 common strata
        # as potential spurious differentia collisions
        assert preceding_common_strata_ranks[0] >= 0
        return preceding_common_strata_ranks[0]
