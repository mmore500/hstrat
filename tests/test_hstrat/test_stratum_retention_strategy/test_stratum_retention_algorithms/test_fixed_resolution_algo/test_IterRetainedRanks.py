import numbers

from iterpop import iterpop as ip
import numpy as np
import pytest

from hstrat._auxiliary_lib import pairwise
from hstrat.hstrat import fixed_resolution_algo


@pytest.mark.parametrize(
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
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
def test_only_dwindling_over_time(fixed_resolution, time_sequence):
    policy = fixed_resolution_algo.Policy(fixed_resolution)
    spec = policy.GetSpec()
    instance = fixed_resolution_algo.IterRetainedRanks(spec)
    for num_strata_deposited in time_sequence:
        for which in (
            instance,
            fixed_resolution_algo.IterRetainedRanks(spec),
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


@pytest.mark.parametrize(
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
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
def test_ranks_sorted_and_unique(fixed_resolution, time_sequence):
    policy = fixed_resolution_algo.Policy(fixed_resolution)
    spec = policy.GetSpec()
    instance = fixed_resolution_algo.IterRetainedRanks(spec)
    for num_strata_deposited in time_sequence:
        for which in (
            instance,
            fixed_resolution_algo.IterRetainedRanks(spec),
        ):
            assert all(
                i < j
                for i, j in pairwise(
                    which(
                        policy,
                        num_strata_deposited,
                    )
                )
            )


@pytest.mark.parametrize(
    "fixed_resolution",
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
        range(10**2),
        (i for i in range(10**2) for __ in range(2)),
        np.random.default_rng(1).integers(
            low=0,
            high=10**3,
            size=10**2,
        ),
    ],
)
def test_zero_and_last_ranks_retained(fixed_resolution, time_sequence):
    policy = fixed_resolution_algo.Policy(fixed_resolution)
    spec = policy.GetSpec()
    instance = fixed_resolution_algo.IterRetainedRanks(spec)
    for num_strata_deposited in time_sequence:
        for which in (
            instance,
            fixed_resolution_algo.IterRetainedRanks(spec),
        ):
            res = which(
                policy,
                num_strata_deposited,
            )
            if num_strata_deposited > 1:
                first, *middle, last = res
                assert first == 0
                assert last == num_strata_deposited - 1
            elif num_strata_deposited == 1:
                assert ip.popsingleton(res) == 0
            else:
                assert next(res, None) is None


@pytest.mark.parametrize(
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
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
def test_ranks_valid(fixed_resolution, time_sequence):
    policy = fixed_resolution_algo.Policy(fixed_resolution)
    spec = policy.GetSpec()
    instance = fixed_resolution_algo.IterRetainedRanks(spec)
    for num_strata_deposited in time_sequence:
        for which in (
            instance,
            fixed_resolution_algo.IterRetainedRanks(spec),
        ):
            assert all(
                isinstance(r, numbers.Integral)
                and 0 <= r < num_strata_deposited
                for r in which(policy, num_strata_deposited)
            )


@pytest.mark.parametrize(
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_eq(fixed_resolution):
    policy = fixed_resolution_algo.Policy(fixed_resolution)
    spec = policy.GetSpec()
    instance = fixed_resolution_algo.IterRetainedRanks(spec)

    assert instance == instance
    assert instance == fixed_resolution_algo.IterRetainedRanks(spec)
    assert instance is not None
