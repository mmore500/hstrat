import typing

from ....._auxiliary_lib import bit_floor
from ._iter_target_recencies import iter_target_recencies


def iter_rank_seps(
    degree: int,
    interspersal: int,
    num_strata_deposited: int,
) -> typing.Iterator[int]:
    """Yield spacing between retained strata for each exponentially-spaced
    coverage target `pow` in ascending order.

    Yielded values will be powers of 2.
    """
    for target_recency in iter_target_recencies(degree, num_strata_deposited):
        # spacing between retained ranks
        target_retained_ranks_sep = max(
            target_recency / interspersal,
            1.0,
        )
        # round down to power of 2
        retained_ranks_sep = bit_floor(int(target_retained_ranks_sep))
        yield retained_ranks_sep
