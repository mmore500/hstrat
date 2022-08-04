import itertools as it
import numpy as np
import pytest

from hstrat2.helpers import pairwise
from hstrat2.hstrat import perfect_resolution_policy


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
def test_only_dwindling_over_time(time_sequence):
    policy = perfect_resolution_policy.Policy()
    spec = policy.GetSpec()
    instance = perfect_resolution_policy.GenDropRanks(spec)
    for num_strata_deposited in time_sequence:
        for which in (
            instance,
            perfect_resolution_policy.GenDropRanks(spec),
        ):
            cur_set = {*which(
                policy,
                num_strata_deposited,
                None,
            )}
            next_set = {*which(
                policy,
                num_strata_deposited + 1,
                None,
            )}
            assert cur_set.issuperset(next_set - {num_strata_deposited})

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
def test_ranks_sorted_and_unique(time_sequence):
    policy = perfect_resolution_policy.Policy()
    spec = policy.GetSpec()
    instance = perfect_resolution_policy.GenDropRanks(spec)
    for num_strata_deposited in time_sequence:
        cur_set = {*policy.IterRetainedRanks(
            num_strata_deposited,
        )}
        for which in (
            instance,
            perfect_resolution_policy.GenDropRanks(spec),
        ):
            assert all(
                i < j
                for i, j in pairwise(which(
                    policy,
                    num_strata_deposited,
                    cur_set,
                ))
            )

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
def test_ranks_valid(time_sequence):
    policy = perfect_resolution_policy.Policy()
    spec = policy.GetSpec()
    instance = perfect_resolution_policy.GenDropRanks(spec)
    for num_strata_deposited in time_sequence:
        cur_set = {*policy.IterRetainedRanks(
            num_strata_deposited,
        )}
        for which in (
            instance,
            perfect_resolution_policy.GenDropRanks(spec),
        ):
            assert all(
                isinstance(r, int)
                and 0 <= r < num_strata_deposited
                for r in which(policy, num_strata_deposited, cur_set)
            )

def test_eq():
    policy = perfect_resolution_policy.Policy()
    spec = policy.GetSpec()
    instance = perfect_resolution_policy.IterRetainedRanks(spec)

    assert instance == instance
    assert instance == perfect_resolution_policy.IterRetainedRanks(spec)
    assert not instance == None
