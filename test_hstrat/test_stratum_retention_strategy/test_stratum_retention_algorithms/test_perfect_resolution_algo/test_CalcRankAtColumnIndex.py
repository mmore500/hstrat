import itertools as it

import numpy as np
import pytest

from hstrat.hstrat import perfect_resolution_algo


@pytest.mark.parametrize(
    "time_sequence",
    [
        range(10**2),
        (i for i in range(10**2) for __ in range(2)),
        np.random.default_rng(1).integers(
            low=0,
            high=10**3,
            size=10**2,
        ),
    ],
)
def test_policy_consistency(time_sequence):
    policy = perfect_resolution_algo.Policy()
    spec = policy.GetSpec()
    instance = perfect_resolution_algo.CalcRankAtColumnIndex(spec)
    for num_strata_deposited in time_sequence:
        for which in (
            instance,
            perfect_resolution_algo.CalcRankAtColumnIndex(spec),
        ):
            assert all(
                calculated == policy_requirement
                for policy_requirement, calculated in it.zip_longest(
                    policy.IterRetainedRanks(num_strata_deposited),
                    (
                        which(policy, i, num_strata_deposited)
                        for i in range(
                            policy.CalcNumStrataRetainedExact(
                                num_strata_deposited,
                            )
                        )
                    ),
                )
            )


def test_eq():
    policy = perfect_resolution_algo.Policy()
    spec = policy.GetSpec()
    instance = perfect_resolution_algo.CalcRankAtColumnIndex(spec)

    assert instance == instance
    assert instance == perfect_resolution_algo.CalcRankAtColumnIndex(spec)
    assert instance is not None
