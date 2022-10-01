import numbers

from iterpop import iterpop as ip
import numpy as np
import pytest

from hstrat._auxiliary_lib import pairwise
from hstrat.hstrat import depth_proportional_resolution_algo


@pytest.mark.parametrize(
    "impl",
    depth_proportional_resolution_algo._scry._IterRetainedRanks_.impls,
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
def test_only_dwindling_over_time(
    impl, depth_proportional_resolution, time_sequence
):
    policy = depth_proportional_resolution_algo.Policy(
        depth_proportional_resolution
    )
    spec = policy.GetSpec()
    instance = impl(spec)
    for num_strata_deposited in time_sequence:
        for which in (
            instance,
            impl(spec),
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
    "impl",
    depth_proportional_resolution_algo._scry._IterRetainedRanks_.impls,
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
def test_ranks_sorted_and_unique(
    impl, depth_proportional_resolution, time_sequence
):
    policy = depth_proportional_resolution_algo.Policy(
        depth_proportional_resolution
    )
    spec = policy.GetSpec()
    instance = impl(spec)
    for num_strata_deposited in time_sequence:
        for which in (
            instance,
            impl(spec),
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
    "impl",
    depth_proportional_resolution_algo._scry._IterRetainedRanks_.impls,
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
def test_zero_and_last_ranks_retained(
    impl, depth_proportional_resolution, time_sequence
):
    policy = depth_proportional_resolution_algo.Policy(
        depth_proportional_resolution
    )
    spec = policy.GetSpec()
    instance = impl(spec)
    for num_strata_deposited in time_sequence:
        for which in (
            instance,
            impl(spec),
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
    "impl",
    depth_proportional_resolution_algo._scry._IterRetainedRanks_.impls,
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
def test_ranks_valid(impl, depth_proportional_resolution, time_sequence):
    policy = depth_proportional_resolution_algo.Policy(
        depth_proportional_resolution
    )
    spec = policy.GetSpec()
    instance = impl(spec)
    for num_strata_deposited in time_sequence:
        for which in (
            instance,
            impl(spec),
        ):
            assert all(
                isinstance(r, numbers.Integral)
                and 0 <= r < num_strata_deposited
                for r in which(policy, num_strata_deposited)
            )


@pytest.mark.parametrize(
    "impl",
    depth_proportional_resolution_algo._scry._IterRetainedRanks_.impls,
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
def test_eq(impl, depth_proportional_resolution):
    policy = depth_proportional_resolution_algo.Policy(
        depth_proportional_resolution
    )
    spec = policy.GetSpec()
    instance = impl(spec)

    assert instance == instance
    assert instance == impl(spec)
    assert instance is not None
