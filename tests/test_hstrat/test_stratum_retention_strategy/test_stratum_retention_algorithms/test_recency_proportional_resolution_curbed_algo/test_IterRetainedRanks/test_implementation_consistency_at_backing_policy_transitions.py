import itertools as it
import typing

import pytest

from hstrat._auxiliary_lib import pairwise
from hstrat.hstrat import recency_proportional_resolution_curbed_algo


def _iter_backing_policy_transition_ranks(
    size_curb: int,
) -> typing.Iterator[int]:

    geom_seq_nth_root_algo_transition_rank = 2 ** (size_curb - 1) + 1
    for i in it.count():
        cur_rank = 2**i
        assert cur_rank.bit_count() == 1

        if cur_rank >= geom_seq_nth_root_algo_transition_rank:
            return geom_seq_nth_root_algo_transition_rank

        yield cur_rank


@pytest.mark.parametrize(
    "size_curb",
    [
        2,
        3,
        7,
        8,
        9,
        42,
        97,
        100,
    ],
)
def test_implementation_consistency_at_backing_policy_transitions(size_curb):
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

        for which1, which2 in pairwise(
            (
                instance,
                recency_proportional_resolution_curbed_algo.IterRetainedRanks(
                    spec
                ),
            )
        ):
            assert {
                *which1(
                    policy,
                    num_strata_deposited,
                )
            } == {
                *which2(
                    policy,
                    num_strata_deposited,
                )
            }
