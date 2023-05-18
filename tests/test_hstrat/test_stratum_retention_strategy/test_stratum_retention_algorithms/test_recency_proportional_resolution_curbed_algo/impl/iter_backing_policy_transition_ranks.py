import itertools as it
import typing

from hstrat import _auxiliary_lib as auxlib
from hstrat.stratum_retention_strategy.stratum_retention_algorithms.recency_proportional_resolution_curbed_algo._impl import (
    calc_geom_seq_nth_root_transition_rank,
    calc_provided_resolution,
)


def iter_backing_policy_transition_ranks(
    size_curb: int,
) -> typing.Iterator[int]:

    gsnra_rank = calc_geom_seq_nth_root_transition_rank(size_curb)
    for i in it.count():
        cur_rank = 2**i
        assert auxlib.popcount(cur_rank) == 1

        if cur_rank >= gsnra_rank:
            if gsnra_rank:
                yield gsnra_rank
            return

        if cur_rank and calc_provided_resolution(
            size_curb, cur_rank - 1
        ) != calc_provided_resolution(size_curb, cur_rank):
            yield cur_rank
        else:
            continue

    assert False
