import typing

from ....._auxiliary_lib import is_nondecreasing
from ._iter_rank_backstops import iter_rank_backstops
from ._iter_rank_seps import iter_rank_seps
from ._iter_target_ranks import iter_target_ranks


def get_retained_ranks(
    degree: int,
    interspersal: int,
    num_strata_deposited: int,
) -> typing.Set[int]:
    """Calculate the set of strata ranks retained at `num_strata_deposited`."""
    # special case
    if num_strata_deposited == 0:
        return set()

    last_rank = num_strata_deposited - 1
    # we will always retain the zeroth rank and the last rank
    # Set data structure prevents duplicates
    res = {0, last_rank}

    for target_rank, rank_backstop, retained_ranks_sep in zip(
        iter_target_ranks(degree, num_strata_deposited),
        iter_rank_backstops(degree, interspersal, num_strata_deposited),
        iter_rank_seps(degree, interspersal, num_strata_deposited),
    ):

        min_retained_rank = rank_backstop

        target_ranks = range(
            min_retained_rank,  # start
            num_strata_deposited,  # stop, not inclusive
            retained_ranks_sep,  # sep
        )

        # sanity checks
        # ensure target_ranks non-empty
        assert len(target_ranks)
        # ensure expected ordering of target ranks
        assert is_nondecreasing(target_ranks)
        # ensure last coverage at or past the target
        assert target_ranks[0] <= target_rank
        # ensure one-past-midpoint coverage before the target
        if len(target_ranks) >= 3:
            assert target_ranks[len(target_ranks) // 2 + 1] > target_rank
        # ensure at least interspersal ranks covered
        try:
            assert len(target_ranks) >= min(
                interspersal,
                len(range(target_rank, num_strata_deposited)),
            )
        except OverflowError:
            pass
        # ensure space complexity cap respected
        assert len(target_ranks) <= 2 * (interspersal + 1)
        # ensure sufficient target_ranks included
        if retained_ranks_sep > 1:
            assert len(target_ranks) >= interspersal

        # add to retained set
        res.update(target_ranks)

    # sanity checks then return
    assert all(0 <= n < num_strata_deposited for n in res)
    assert res
    return res
