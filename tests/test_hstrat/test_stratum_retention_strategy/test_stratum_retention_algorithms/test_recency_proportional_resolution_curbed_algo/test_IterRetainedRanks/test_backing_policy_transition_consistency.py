import pytest

from hstrat.hstrat import recency_proportional_resolution_curbed_algo

from ..impl import iter_backing_policy_transition_ranks


@pytest.mark.parametrize(
    "size_curb",
    [
        1,
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
        42,
        97,
        100,
        254,
        255,
        256,
        257,
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
        for transition_rank in iter_backing_policy_transition_ranks(size_curb)
        for test_rank in range(
            max(transition_rank - 2, 0), transition_rank + 3
        )
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
            assert cur_set.issuperset(next_set - {num_strata_deposited})
