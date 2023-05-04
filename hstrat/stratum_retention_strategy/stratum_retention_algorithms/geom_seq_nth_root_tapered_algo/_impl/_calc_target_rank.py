import math

from ._calc_target_recency import calc_target_recency


def calc_target_rank(
    degree: int,
    pow_: int,
    num_strata_deposited: int,
) -> int:
    """What should the rank of the `pow`th exponentially-spaced-back-from-
    recency-zero target be?

    Will monotonically increase with `num_strata_deposited`.
    """
    target_recency = calc_target_recency(degree, pow_, num_strata_deposited)
    recency_cutoff = target_recency
    rank_cutoff = max(
        num_strata_deposited - int(math.ceil(recency_cutoff)),
        0,
    )
    if num_strata_deposited == 0:
        assert rank_cutoff == 0
    else:
        assert 0 <= rank_cutoff <= num_strata_deposited - 1
    return rank_cutoff
