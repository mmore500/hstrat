import itertools as it

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
def test_policy_consistency(size_curb, time_sequence):
    policy = recency_proportional_resolution_curbed_algo.Policy(size_curb)
    spec = policy.GetSpec()
    instance = (
        recency_proportional_resolution_curbed_algo.CalcRankAtColumnIndex(spec)
    )
    for num_strata_deposited in time_sequence:
        for which in (
            instance,
            recency_proportional_resolution_curbed_algo.CalcRankAtColumnIndex(
                spec
            ),
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
def test_eq(size_curb):
    policy = recency_proportional_resolution_curbed_algo.Policy(size_curb)
    spec = policy.GetSpec()
    instance = (
        recency_proportional_resolution_curbed_algo.CalcRankAtColumnIndex(spec)
    )

    assert instance == instance
    assert (
        instance
        == recency_proportional_resolution_curbed_algo.CalcRankAtColumnIndex(
            spec
        )
    )
    assert instance is not None
