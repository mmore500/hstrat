import math

from ._calc_target_rank import calc_target_rank
from ._calc_target_recency import calc_target_recency


def calc_rank_cutoff(
    degree: int,
    interspersal: int,
    pow_: int,
    num_strata_deposited: int,
) -> int:
    """Before what rank should no strata be retained to provide coverage for the `pow`th target recency?

    Will be less than target rank to ensure adequate resolution at target
    rank and just greater than target rank. Inclusive (i.e., this rank may
    be retained). Will monotonically increase with num_strata_deposited.
    """
    target_recency = calc_target_recency(
        degree,
        pow_,
        num_strata_deposited,
    )
    rank_cutoff = max(
        num_strata_deposited
        - int(math.ceil(target_recency * (interspersal + 1) / interspersal)),
        0,
    )
    assert rank_cutoff <= calc_target_rank(
        degree,
        pow_,
        num_strata_deposited,
    )
    if num_strata_deposited == 0:
        assert rank_cutoff == 0
    else:
        assert 0 <= rank_cutoff <= num_strata_deposited - 1
    return rank_cutoff
