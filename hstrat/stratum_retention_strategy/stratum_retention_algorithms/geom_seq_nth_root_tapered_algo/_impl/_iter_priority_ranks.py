import typing

import interval_search as inch

from ....._auxiliary_lib import div_range, memoize_generator
from ._calc_rank_backstop import calc_rank_backstop
from ._calc_rank_sep import calc_rank_sep


@memoize_generator()
def iter_priority_ranks(
    degree: int,
    interspersal: int,
    pow_: int,
    num_strata_deposited: int,
) -> typing.Iterator[int]:
    """Iterate over retained ranks for the `pow`th target recency.

    Ranks are yielded from last-to-be-deleted to first-to-be-deleted. The
    very-first-to-be-deleted (i.e., lowest priority) rank is yielded last. Will
    yield all ranks less than `num_strata_deposited` before exhaustion.

    Notes
    -----
    May yield duplicates (i.e., yield rank x then later again yield rank x).
    This is acceptable in the internal use case because rank priority only
    depends on its soonest position in the stream of yielded values.
    Subsequent yieldings have no effect because the generator is sampled until
    exhausted or an unseen rank is yielded.
    """
    # aliases for terseness
    d = degree
    i = interspersal

    min_retained_rank = calc_rank_backstop(d, i, pow_, num_strata_deposited)
    retained_ranks_sep = calc_rank_sep(d, i, pow_, num_strata_deposited)

    if pow_ == 0:
        # optimization
        yield from reversed(range(num_strata_deposited))
        return
    elif pow_ == degree:
        # the highest-degree pow always tracks strata 0
        # and the biggest relevant sep for strata 0 is infinite.
        # i.e., the backstop for highest-debree pow is always strata 0
        # So, we need a special case for this pow.
        # However, because strata 0 is retained indefinitely, we actually
        # only need to worry about the next retained strata,
        # which is at retained_ranks_sep.
        # Thus, we use calc_rank_sep instead of calc_rank_backstop.
        # TODO can this doubling search be done in constant time?
        biggest_relevant_rank = inch.doubling_search(
            lambda x: calc_rank_sep(d, i, pow_, x + 1) >= num_strata_deposited,
            num_strata_deposited,
        )
        biggest_relevant_sep = calc_rank_sep(
            degree,
            interspersal,
            pow_,
            biggest_relevant_rank,
        )

    else:
        # TODO can this doubling search be done in constant time?
        biggest_relevant_rank = inch.doubling_search(
            lambda x: calc_rank_backstop(d, i, pow_, x + 1)
            >= num_strata_deposited,
            num_strata_deposited,
        )
        biggest_relevant_sep = calc_rank_sep(
            degree,
            interspersal,
            pow_,
            biggest_relevant_rank,
        )

    # in practice, just "cur_sep == retained_ranks * 2" appears required
    # i.e., tests pass with
    #
    # for cur_sep in retained_ranks_sep * 2,:
    #
    # TODO can this be proven?
    for cur_sep in div_range(
        biggest_relevant_sep,  # start
        retained_ranks_sep,  # stop, non-inclusive
        2,  # iteration action: divide by 2
    ):
        # TODO can this doubling search be done in constant time?
        cur_sep_rank = inch.doubling_search(
            lambda x: calc_rank_sep(d, i, pow_, x) >= cur_sep,
            # cur_sep is always guaranteed at least leq its threshold
            # num_strata_deposited, so we can safely begin searching for its
            # threshold at cur_sep
            # (look at calc_rank_sep to convince yourself)
            # this optimization reduces necessary search steps and prevents
            # exceedance of maximum recursion depth in some tests
            max(num_strata_deposited, cur_sep),
        )
        cur_sep_rank_backstop = calc_rank_backstop(
            degree,
            interspersal,
            pow_,
            cur_sep_rank,
        )

        yield from reversed(
            range(
                cur_sep_rank_backstop,  # start
                # +1 to be inclusive of cur_sep_rank
                min(cur_sep_rank + 1, num_strata_deposited),  # stop
                cur_sep,  # sep
            )
        )

    # TODO somehow exclude duplicates with above for better efficiency?
    yield from reversed(
        range(
            min_retained_rank,  # start
            num_strata_deposited,  # stop, non-inclusive
            retained_ranks_sep,  # sep
        )
    )

    # recurse
    if retained_ranks_sep == 1:
        # base case
        yield from reversed(
            range(
                0,
                min_retained_rank,
            )
        )
        return

    prev_sep_rank = inch.binary_search(
        lambda x: calc_rank_sep(d, i, pow_, x + 1) >= retained_ranks_sep,
        0,
        num_strata_deposited - 1,
    )
    yield from range(
        min_retained_rank,  # start
        prev_sep_rank,  # stop, not inclusive
        -retained_ranks_sep,  # sep
    )
    assert prev_sep_rank < num_strata_deposited
    yield from iter_priority_ranks(
        degree,
        interspersal,
        pow_,
        # + 1 due to apparent off-by-one error w/ just prev_sep_rank
        # where rank 5984 isn't properly retained
        # with degree 9, interspersal 2 @ generation 6405
        # on get_retained_ranks test case
        min(prev_sep_rank + 1, num_strata_deposited - 1),
    )
