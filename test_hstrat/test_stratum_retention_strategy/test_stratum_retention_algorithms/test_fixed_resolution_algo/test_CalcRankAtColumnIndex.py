import itertools as it

import numpy as np
import pytest

from hstrat._testing import iter_ftor_shims
from hstrat.hstrat import fixed_resolution_algo


@pytest.mark.parametrize(
    "impl",
    fixed_resolution_algo._scry._CalcRankAtColumnIndex_.impls,
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
def test_policy_consistency(impl, fixed_resolution, time_sequence):
    policy = fixed_resolution_algo.Policy(fixed_resolution)
    spec = policy.GetSpec()
    instance = impl(spec)
    for num_strata_deposited in time_sequence:
        for which in (
            instance,
            impl(spec),
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
    "impl",
    fixed_resolution_algo._scry._CalcRankAtColumnIndex_.impls,
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
def test_eq(impl, fixed_resolution):
    policy = fixed_resolution_algo.Policy(fixed_resolution)
    spec = policy.GetSpec()
    instance = impl(spec)

    assert instance == instance
    assert instance == impl(spec)
    assert instance is not None


@pytest.mark.parametrize(
    "rep",
    range(20),
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
def test_impl_consistency(rep, fixed_resolution):
    policy = fixed_resolution_algo.Policy(fixed_resolution)
    spec = policy.GetSpec()

    rng = np.random.default_rng(rep)

    for num_strata_deposited in (
        rng.integers(1, 2**5),
        rng.integers(1, 2**10),
        rng.integers(1, 2**32),
    ):
        for index in (
            0,
            policy.CalcNumStrataRetainedExact(num_strata_deposited) - 1,
            rng.integers(
                0, policy.CalcNumStrataRetainedExact(num_strata_deposited)
            ),
        ):
            assert (
                len(
                    {
                        impl(spec)(
                            policy,
                            index,
                            num_strata_deposited,
                        )
                        for impl in it.chain(
                            fixed_resolution_algo._scry._CalcRankAtColumnIndex_.impls,
                            iter_ftor_shims(
                                lambda p: p.CalcRankAtColumnIndex,
                                fixed_resolution_algo._Policy_.impls,
                            ),
                        )
                    }
                )
                == 1
            )
