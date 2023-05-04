from ._calc_rank_cutoff import calc_rank_cutoff
from ._calc_rank_sep import calc_rank_sep
from ._calc_target_rank import calc_target_rank


def calc_rank_backstop(
    degree: int,
    interspersal: int,
    pow_: int,
    num_strata_deposited: int,
) -> int:
    """What should the most ancient rank retained to cover the `pow`th target
    recency be?

    This rank and all subsequent ranks spaced forward by `_calc_rank_sep`
    positions through recency zero will be retained. Will monotonically
    increase with `num_strata_deposited` and be an even multiple of
    `_calc_rank_sep`.
    """
    rank_cutoff = calc_rank_cutoff(
        degree,
        interspersal,
        pow_,
        num_strata_deposited,
    )
    retained_ranks_sep = calc_rank_sep(
        degree,
        interspersal,
        pow_,
        num_strata_deposited,
    )

    # round UP from rank_cutoff
    # to align evenly with retained_ranks_sep
    # adapted from https://stackoverflow.com/a/14092788
    min_retained_rank = rank_cutoff - (rank_cutoff % -retained_ranks_sep)
    assert min_retained_rank % retained_ranks_sep == 0
    assert min_retained_rank >= rank_cutoff

    # check that even with rounding up, we are still covering the target
    # rank
    # i.e., that the most ancient retained rank (the backstop rank) falls
    # before the target rank so that the target rank is guaranteed within
    # a _calc_rank_sep window
    assert min_retained_rank <= calc_target_rank(
        degree, pow_, num_strata_deposited
    )

    # more sanity checks on range of output value
    if num_strata_deposited == 0:
        assert min_retained_rank == 0
    else:
        assert 0 <= min_retained_rank <= num_strata_deposited - 1

    # backstop rank synonomous w/ the most ancient (min) retained rank
    return min_retained_rank
