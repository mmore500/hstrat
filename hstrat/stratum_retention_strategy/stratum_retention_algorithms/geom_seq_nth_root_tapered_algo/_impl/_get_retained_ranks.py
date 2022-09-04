import functools
import typing

from ..._detail import PolicyCouplerBase
from ._iter_priority_ranks import iter_priority_ranks


@functools.lru_cache(maxsize=512)
def get_retained_ranks(
    policy: PolicyCouplerBase,
    num_strata_deposited: int,
) -> typing.Set[int]:
    """Calculate the set of strata ranks retained at `num_strata_deposited`."""
    spec = policy.GetSpec()
    degree = spec.GetDegree()
    interspersal = spec.GetInterspersal()

    # special case
    if num_strata_deposited == 0:
        return set()

    last_rank = num_strata_deposited - 1
    # we will always retain the zeroth rank and the last rank
    # Set data structure prevents duplicates
    res = {0, last_rank}

    # create iterators that yield ranks for retention in priority order for
    # each target recency
    iters = [
        iter_priority_ranks(degree, interspersal, pow, num_strata_deposited)
        # note:
        # even though 0th pow is always just the most recent rank
        # we need to iterate over it because it will eventually yield
        # all preceding ranks ensuring that we fill available space
        # HOWEVER, it is excluded from the first round and is only drawn
        # from subsequently to ensure that it will have lowest priority
        # thereby making optimizations easier [and requiring less space
        # be devoted to the equivalent of
        # reversed(range(num_strata_deposited))]
        for pow in reversed(range(1, degree + 1))
    ]
    # round robin, taking at least one rank from each iterator until the
    # upper bound on space complexity is exactly reached or all iterators
    # are exhausted
    while len(res) < policy.CalcNumStrataRetainedUpperBound(
        num_strata_deposited,
    ):
        res_before = len(res)
        for iter_ in iters:
            # will loop 0 times if iter_ is empty
            for priority_rank in iter_:
                # draw from iter_ until a rank not already in res is
                # discovered or iter_ is exhausted
                if priority_rank not in res:
                    res.add(priority_rank)
                    break
            # ensure space complexity limit is not exceeded
            if len(res) == policy.CalcNumStrataRetainedUpperBound(
                num_strata_deposited,
            ):
                break
        # if no progress was made then all iter_ were empty
        # and its time to quit
        if res_before == len(res):
            break

    # draw from pow 0 iter until res full
    # (pow 0 iter only drawn from if all other iters are exhausted)
    for priority_rank in iter_priority_ranks(
        degree, interspersal, 0, num_strata_deposited
    ):
        # ensure space complexity limit is not exceeded
        if len(res) == policy.CalcNumStrataRetainedUpperBound(
            num_strata_deposited,
        ):
            break
        res.add(priority_rank)

    # sanity checks then return
    assert all(0 <= n < num_strata_deposited for n in res)
    assert len(res) <= policy.CalcNumStrataRetainedUpperBound(
        num_strata_deposited,
    )
    assert len(res) == policy.CalcNumStrataRetainedExact(num_strata_deposited)
    assert res
    if len(res) < policy.CalcNumStrataRetainedUpperBound(
        num_strata_deposited,
    ):
        assert res == {*range(len(res))}

    return res
