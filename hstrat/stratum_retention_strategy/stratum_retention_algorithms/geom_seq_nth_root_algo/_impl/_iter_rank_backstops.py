import typing

from ._iter_rank_cutoffs import iter_rank_cutoffs
from ._iter_rank_seps import iter_rank_seps
from ._iter_target_ranks import iter_target_ranks


def iter_rank_backstops(
    degree: int,
    interspersal: int,
    num_strata_deposited: int,
) -> typing.Iterator[int]:
    """Yield most ancient retained rank for each exponentially-spaced
    coverage target `pow` in ascending order.

    All subsequent ranks spaced forward by `_calc_rank_sep`
    positions through recency zero will be retained. Will monotonically
    increase with `num_strata_deposited` and be an even multiple of
    `_calc_rank_sep`.
    """
    for rank_cutoff, retained_ranks_sep, target_rank in zip(
        iter_rank_cutoffs(degree, interspersal, num_strata_deposited),
        iter_rank_seps(degree, interspersal, num_strata_deposited),
        iter_target_ranks(degree, num_strata_deposited),
    ):

        # round UP from rank_cutoff
        # to align evenly with retained_ranks_sep
        # adapted from https://stackoverflow.com/a/14092788
        min_retained_rank = rank_cutoff - (rank_cutoff % -retained_ranks_sep)
        assert min_retained_rank % retained_ranks_sep == 0
        assert min_retained_rank >= rank_cutoff

        # check that even with rounding up, we are still covering the
        # target rank
        # i.e., that the most ancient retained rank (the backstop rank)
        # falls before the target rank so that the target rank is
        # guaranteed within an _iter_rank_sep window
        assert min_retained_rank <= target_rank

        # more sanity checks on range of return value
        if num_strata_deposited == 0:
            assert min_retained_rank == 0
        else:
            assert 0 <= min_retained_rank <= num_strata_deposited - 1

        # backstop rank synonomous w/ the most ancient (min) retained rank
        yield min_retained_rank
