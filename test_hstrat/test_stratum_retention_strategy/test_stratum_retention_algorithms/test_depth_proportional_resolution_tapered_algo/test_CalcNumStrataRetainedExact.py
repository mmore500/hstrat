import numpy as np
import pytest

from hstrat.hstrat import depth_proportional_resolution_tapered_algo


@pytest.mark.parametrize(
    "depth_proportional_resolution",
    [
        1,
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
            size=10**2,
        ),
        (2**32,),
    ],
)
def test_policy_consistency(depth_proportional_resolution, time_sequence):
    policy = depth_proportional_resolution_tapered_algo.Policy(
        depth_proportional_resolution
    )
    spec = policy.GetSpec()
    instance = (
        depth_proportional_resolution_tapered_algo.CalcNumStrataRetainedExact(
            spec
        )
    )
    for num_strata_deposited in time_sequence:
        policy_requirement = len(
            [
                *policy.IterRetainedRanks(
                    num_strata_deposited,
                )
            ]
        )
        for which in (
            instance,
            depth_proportional_resolution_tapered_algo.CalcNumStrataRetainedExact(
                spec
            ),
        ):
            assert (
                which(
                    policy,
                    num_strata_deposited,
                )
                == policy_requirement
            )


@pytest.mark.parametrize(
    "depth_proportional_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_eq(depth_proportional_resolution):
    policy = depth_proportional_resolution_tapered_algo.Policy(
        depth_proportional_resolution
    )
    spec = policy.GetSpec()
    instance = (
        depth_proportional_resolution_tapered_algo.CalcNumStrataRetainedExact(
            spec
        )
    )

    assert instance == instance
    assert (
        instance
        == depth_proportional_resolution_tapered_algo.CalcNumStrataRetainedExact(
            spec,
        )
    )
    assert instance is not None
