import numpy as np
import pytest

from hstrat.hstrat import recency_proportional_resolution_curbed_algo


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
        42,
        97,
        100,
        254,
        255,
        256,
        257,
    ],
)
@pytest.mark.parametrize(
    "time_sequence",
    [
        range(10**3),
        (i for i in range(10**2) for __ in range(2)),
        np.random.default_rng(1).integers(
            low=0,
            high=2**32,
            size=10,
        ),
        (2**32,),
    ],
)
def test_policy_consistency(size_curb, time_sequence):
    policy = recency_proportional_resolution_curbed_algo.Policy(size_curb)
    spec = policy.GetSpec()
    instance = recency_proportional_resolution_curbed_algo.GenDropRanks(spec)
    for num_strata_deposited in time_sequence:
        policy_requirement = {
            *policy.IterRetainedRanks(
                num_strata_deposited,
            )
        } - {
            *policy.IterRetainedRanks(
                num_strata_deposited + 1,
            )
        }
        for which in (
            instance,
            recency_proportional_resolution_curbed_algo.GenDropRanks(spec),
        ):
            assert sorted(
                which(
                    policy,
                    num_strata_deposited,
                    policy.IterRetainedRanks(num_strata_deposited),
                )
            ) == sorted(policy_requirement), (
                num_strata_deposited,
                size_curb,
                which,
            )
