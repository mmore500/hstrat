import itertools as it
import typing

import pytest

from hstrat._auxiliary_lib import pairwise, popcount
from hstrat.hstrat import recency_proportional_resolution_curbed_algo


def _iter_backing_policy_transition_ranks(
    size_curb: int,
) -> typing.Iterator[int]:

    geom_seq_nth_root_algo_transition_rank = 2 ** (size_curb - 1) + 1
    for i in it.count():
        cur_rank = 2**i
        assert popcount(cur_rank) == 1

        if cur_rank >= geom_seq_nth_root_algo_transition_rank:
            return geom_seq_nth_root_algo_transition_rank

        yield cur_rank


@pytest.mark.parametrize(
    "size_curb",
    [
        1,
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
        for test_rank in range(
            max(transition_rank - 2, 0), transition_rank + 3
        )
    ):

        for which1, which2 in pairwise(
            (
                instance,
                recency_proportional_resolution_curbed_algo.IterRetainedRanks(
                    spec
                ),
            )
        ):
            # fmt: off
            # black bug in 2022.{10,12}.0 misformats {*x}
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
            # fmt: on
