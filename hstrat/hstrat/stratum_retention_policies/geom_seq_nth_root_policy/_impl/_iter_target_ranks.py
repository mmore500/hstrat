import math
import typing

from ._iter_target_recencies import iter_target_recencies


def iter_target_ranks(
    degree: int,
    num_strata_deposited: int,
) -> typing.Iterator[int]:
    """Yield strata ranks for each exponentially-spaced coverage target
    `pow` in ascending order."""
    for target_recency in iter_target_recencies(degree, num_strata_deposited):
        recency_cutoff = target_recency
        rank_cutoff = max(
            num_strata_deposited - int(math.ceil(recency_cutoff)),
            0,
        )
        if num_strata_deposited == 0:
            assert rank_cutoff == 0
        else:
            assert 0 <= rank_cutoff <= num_strata_deposited - 1
        yield rank_cutoff
