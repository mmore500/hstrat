import numpy as np
import pytest

from hstrat2.hstrat import geom_seq_nth_root_policy


@pytest.mark.parametrize(
    'degree',
    [
        1,
        2,
        3,
        7,
        9,
        42,
        100,
    ],
)
@pytest.mark.parametrize(
    'interspersal',
    [
        1,
        2,
        5,
    ],
)
@pytest.mark.parametrize(
    'time_sequence',
    [
        range(10**4),
        (i for i in range(10**2) for __ in range(2)),
        np.random.default_rng(1).integers(
            low=0,
            high=2**32,
            size=10**2,
        ),
    ],
)
def test_policy_consistency(degree, interspersal, time_sequence):
    policy = geom_seq_nth_root_policy.Policy(degree, interspersal)
    spec = policy.GetSpec()
    instance = geom_seq_nth_root_policy.CalcNumStrataRetainedExact(spec)
    for num_strata_deposited in time_sequence:
        policy_requirement = len([*policy.IterRetainedRanks(
            num_strata_deposited,
        )])
        for which in (
            instance,
            geom_seq_nth_root_policy.CalcNumStrataRetainedExact(spec),
        ):
            assert which(
                policy,
                num_strata_deposited,
            ) == policy_requirement

@pytest.mark.parametrize(
    'degree',
    [
        1,
        2,
        3,
        7,
        9,
        42,
        100,
    ],
)
@pytest.mark.parametrize(
    'interspersal',
    [
        1,
        2,
        5,
    ],
)
def test_eq(degree, interspersal):
    policy = geom_seq_nth_root_policy.Policy(degree, interspersal)
    spec = policy.GetSpec()
    instance = geom_seq_nth_root_policy.CalcNumStrataRetainedExact(spec)

    assert instance == instance
    assert instance == geom_seq_nth_root_policy.CalcNumStrataRetainedExact(
        spec,
    )
    assert not instance == None
