import itertools as it

import numpy as np
import pytest

from hstrat._testing import iter_ftor_shims, iter_no_calcrank_ftor_shims
from hstrat.hstrat import fixed_resolution_algo
from hstrat.stratum_retention_strategy.stratum_retention_algorithms._impl import (
    CalcMrcaUncertaintyRelUpperBoundPessimalRankBruteForce,
)


@pytest.mark.parametrize(
    "impl",
    fixed_resolution_algo._invar._CalcMrcaUncertaintyRelUpperBoundPessimalRank_.impls,
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
        np.random.default_rng(1).integers(
            10**2,
            size=10,
        ),
        np.random.default_rng(1).integers(
            10**3,
            size=10,
        ),
    ],
)
def test_policy_consistency(impl, fixed_resolution, time_sequence):
    policy = fixed_resolution_algo.Policy(fixed_resolution)
    spec = policy.GetSpec()
    instance = impl(spec)
    for num_strata_deposited_a in time_sequence:
        for num_strata_deposited_b in (
            num_strata_deposited_a // 3,
            num_strata_deposited_a // 2,
            num_strata_deposited_a,
            num_strata_deposited_a + 1,
            num_strata_deposited_a + 10,
            num_strata_deposited_a + 100,
        ):
            if 0 in (num_strata_deposited_a, num_strata_deposited_b):
                continue
            for actual_mrca_rank in np.random.default_rng(1).integers(
                min(num_strata_deposited_a, num_strata_deposited_b),
                size=3,
            ):
                policy_requirement = policy.CalcMrcaUncertaintyRelUpperBound(
                    num_strata_deposited_a,
                    num_strata_deposited_b,
                    CalcMrcaUncertaintyRelUpperBoundPessimalRankBruteForce()(
                        policy,
                        num_strata_deposited_a,
                        num_strata_deposited_b,
                    ),
                )
                for which in (
                    instance,
                    impl(spec),
                ):
                    assert (
                        policy.CalcMrcaUncertaintyRelUpperBound(
                            num_strata_deposited_a,
                            num_strata_deposited_b,
                            which(
                                policy,
                                num_strata_deposited_a,
                                num_strata_deposited_b,
                            ),
                        )
                        == policy_requirement
                    )


@pytest.mark.parametrize(
    "impl",
    fixed_resolution_algo._invar._CalcMrcaUncertaintyRelUpperBoundPessimalRank_.impls,
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

    for num_strata_deposited_a in (
        rng.integers(1, 2**5),
        rng.integers(1, 2**10),
        rng.integers(1, 2**32),
    ):
        for num_strata_deposited_b in (
            num_strata_deposited_a,
            num_strata_deposited_a + 107,
            rng.integers(1, num_strata_deposited_a + 1),
        ):
            bound = min(num_strata_deposited_a, num_strata_deposited_b)
            assert (
                len(
                    {
                        impl(spec)(
                            policy,
                            num_strata_deposited_a,
                            num_strata_deposited_b,
                        )
                        for impl in it.chain(
                            fixed_resolution_algo._invar._CalcMrcaUncertaintyRelUpperBoundPessimalRank_.impls,
                            iter_ftor_shims(
                                lambda p: p.CalcMrcaUncertaintyRelUpperBoundPessimalRank,
                                fixed_resolution_algo._Policy_.impls,
                            ),
                            iter_no_calcrank_ftor_shims(
                                lambda p: p.CalcMrcaUncertaintyRelUpperBoundPessimalRank,
                                fixed_resolution_algo._Policy_.impls,
                            ),
                        )
                    }
                )
                == 1
            )
