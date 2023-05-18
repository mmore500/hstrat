import numpy as np
import pytest

from hstrat.hstrat import recency_proportional_resolution_curbed_algo


@pytest.mark.parametrize(
    "size_curb",
    [
        2,
        3,
        7,
        42,
        97,
        100,
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
def test_only_dwindling_over_time(size_curb, time_sequence):
    policy = recency_proportional_resolution_curbed_algo.Policy(size_curb)
    spec = policy.GetSpec()
    instance = recency_proportional_resolution_curbed_algo.IterRetainedRanks(
        spec
    )
    for num_strata_deposited in time_sequence:
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
            assert cur_set.issuperset(next_set - {num_strata_deposited})
