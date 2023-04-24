import itertools as it

import numpy as np
import pytest

from hstrat._testing import iter_ftor_shims, iter_no_calcrank_ftor_shims
from hstrat.hstrat import fixed_resolution_algo


@pytest.mark.parametrize(
    "impl",
    fixed_resolution_algo._invar._CalcMrcaUncertaintyRelUpperBound_.impls,
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
            high=2**32,
            size=10**2,
        ),
    ],
)
def test_policy_consistency(impl, fixed_resolution, time_sequence):
    policy = fixed_resolution_algo.Policy(fixed_resolution)
    spec = policy.GetSpec()
    instance = impl(spec)
    for num_strata_deposited in time_sequence:
        for actual_mrca_rank in (
            np.random.default_rng(num_strata_deposited,).integers(
                low=0,
                high=num_strata_deposited,
                size=10**2,
            )
            if num_strata_deposited
            else iter(())
        ):
            policy_requirement = policy.CalcMrcaUncertaintyRelExact(
                num_strata_deposited,
                num_strata_deposited,
                actual_mrca_rank,
            )
            for which in (
                instance,
                impl(spec),
            ):
                assert (
                    which(
                        policy,
                        num_strata_deposited,
                        num_strata_deposited,
                        actual_mrca_rank,
                    )
                    >= policy_requirement
                )


@pytest.mark.parametrize(
    "impl",
    fixed_resolution_algo._invar._CalcMrcaUncertaintyRelUpperBound_.impls,
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
    "impl",
    fixed_resolution_algo._invar._CalcMrcaUncertaintyRelUpperBound_.impls,
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
def test_negative_index(impl, fixed_resolution):
    policy = fixed_resolution_algo.Policy(fixed_resolution)
    spec = policy.GetSpec()
    instance = impl(spec)

    for diff in range(1, 100):
        assert instance(policy, 100, 100, -diff,) == instance(
            policy,
            100,
            100,
            99 - diff,
        )

        assert instance(policy, 101, 100, -diff,) == instance(
            policy,
            101,
            100,
            99 - diff,
        )

        assert instance(policy, 150, 100, -diff,) == instance(
            policy,
            150,
            100,
            99 - diff,
        )

        assert instance(policy, 100, 101, -diff,) == instance(
            policy,
            101,
            100,
            99 - diff,
        )

        assert instance(policy, 100, 150, -diff,) == instance(
            policy,
            150,
            100,
            99 - diff,
        )


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
            for actual_mrca_rank in [0, bound - 1, rng.integers(bound)]:
                assert (
                    len(
                        {
                            impl(spec)(
                                policy,
                                num_strata_deposited_a,
                                num_strata_deposited_b,
                                actual_mrca_rank,
                            )
                            for impl in it.chain(
                                fixed_resolution_algo._invar._CalcMrcaUncertaintyRelUpperBound_.impls,
                                iter_ftor_shims(
                                    lambda p: p.CalcMrcaUncertaintyRelUpperBound,
                                    fixed_resolution_algo._Policy_.impls,
                                ),
                                iter_no_calcrank_ftor_shims(
                                    lambda p: p.CalcMrcaUncertaintyRelUpperBound,
                                    fixed_resolution_algo._Policy_.impls,
                                ),
                            )
                        }
                    )
                    == 1
                )
