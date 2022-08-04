import numpy as np
import pytest

from hstrat2.hstrat import nominal_resolution_policy


@pytest.mark.parametrize(
    'time_sequence',
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
    policy = nominal_resolution_policy.Policy()
    spec = policy.GetSpec()
    instance = nominal_resolution_policy.CalcNumStrataRetainedExact(spec)
    for num_strata_deposited in time_sequence:
        policy_requirement = len([*policy.IterRetainedRanks(
            num_strata_deposited,
        )])
        for which in (
            instance,
            nominal_resolution_policy.CalcNumStrataRetainedExact(spec),
        ):
            assert which(
                policy,
                num_strata_deposited,
            ) == policy_requirement

def test_eq():
    policy = nominal_resolution_policy.Policy()
    spec = policy.GetSpec()
    instance = nominal_resolution_policy.CalcNumStrataRetainedExact(spec)

    assert instance == instance
    assert instance == nominal_resolution_policy.CalcNumStrataRetainedExact(
        spec,
    )
    assert not instance == None
