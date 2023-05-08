import itertools as it
import typing

import numpy as np
import pytest

from hstrat.hstrat import recency_proportional_resolution_curbed_algo


def _iter_backing_policy_transition_ranks(
    size_curb: int,
) -> typing.Iterator[int]:

    geom_seq_nth_root_algo_transition_rank = 2 ** (size_curb - 1) + 1
    for i in it.count():
        cur_rank = 2**i
        assert cur_rank.bit_count() == 1

        if cur_rank >= geom_seq_nth_root_algo_transition_rank:
            # return geom_seq_nth_root_algo_transition_rank
            return

        yield cur_rank


@pytest.mark.parametrize(
    "size_curb",
    [
        2,
        3,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        # 42,
        # 97,
        # 100,
    ],
)
def test_backing_policy_transition_consistency(size_curb):
    policy = recency_proportional_resolution_curbed_algo.Policy(size_curb)
    spec = policy.GetSpec()
    instance = recency_proportional_resolution_curbed_algo.IterRetainedRanks(
        spec
    )

    for num_strata_deposited in (
        test_rank
        for transition_rank in _iter_backing_policy_transition_ranks(size_curb)
        for test_rank in range(transition_rank - 2, transition_rank + 3)
    ):
        for which in (
            instance,
            recency_proportional_resolution_curbed_algo.IterRetainedRanks(
                spec
            ),
        ):
            cur_set = {
                *which(
                    policy,
                    num_strata_deposited,
                )
            }
            next_set = {
                *which(
                    policy,
                    num_strata_deposited + 1,
                )
            }
            assert (next_set - {num_strata_deposited}) - cur_set == set()
            assert cur_set.issuperset(next_set - {num_strata_deposited}), size_curb
