from ....._auxiliary_lib import bit_floor
from ._calc_target_recency import calc_target_recency


def calc_rank_sep(
    degree: int,
    interspersal: int,
    pow_: int,
    num_strata_deposited: int,
) -> int:
    """How far apart should ranks retained to cover the `pow`th target recency
    be spaced?

    Will be a power of 2 monotonically increasing with `num_strata_deposited`.
    """
    target_recency = calc_target_recency(degree, pow_, num_strata_deposited)
    # spacing between retained ranks
    target_retained_ranks_sep = max(
        target_recency / interspersal,
        1.0,
    )
    # round down to power of 2
    retained_ranks_sep = bit_floor(int(target_retained_ranks_sep))
    return retained_ranks_sep
