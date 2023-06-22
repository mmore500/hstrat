import itertools as it

import numpy as np
import pytest

from hstrat._testing import iter_ftor_shims, iter_no_calcrank_ftor_shims
from hstrat.hstrat import fixed_resolution_algo


@pytest.mark.parametrize(
    "impl",
    fixed_resolution_algo._scry._CalcMrcaUncertaintyAbsExact_.impls,
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
        retained_ranks = np.fromiter(
            policy.IterRetainedRanks(num_strata_deposited),
            int,
        )
        for actual_mrca_rank in range(num_strata_deposited):
            last_known_commonality = retained_ranks[
                retained_ranks <= actual_mrca_rank,
            ].max(
                initial=0,
            )
            first_known_disparity = retained_ranks[
                retained_ranks > actual_mrca_rank,
            ].min(
                initial=num_strata_deposited,
            )
            policy_requirement = (
                first_known_disparity - last_known_commonality - 1
            )
            assert policy_requirement >= 0
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
                    == policy_requirement
                )


@pytest.mark.parametrize(
    "impl",
    fixed_resolution_algo._scry._CalcMrcaUncertaintyAbsExact_.impls,
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
def test_policy_consistency_uneven_branches(impl, fixed_resolution):
    policy = fixed_resolution_algo.Policy(fixed_resolution)
    spec = policy.GetSpec()
    instance = impl(spec)
    sample_durations = it.chain(
        range(10**2),
        np.logspace(7, 16, num=10, base=2, dtype="int"),
    )
    for num_strata_deposited_a in sample_durations:
        ranks_a = set(policy.IterRetainedRanks(num_strata_deposited_a))
        for num_strata_deposited_b in sample_durations:
            ranks_b = set(policy.IterRetainedRanks(num_strata_deposited_b))
            retained_ranks = np.fromiter(ranks_a & ranks_b, int)
            least_num_strata_deposited = min(
                num_strata_deposited_a,
                num_strata_deposited_b,
            )
            for actual_mrca_rank in range(least_num_strata_deposited):
                last_known_commonality = retained_ranks[
                    retained_ranks <= actual_mrca_rank,
                ].max(
                    initial=0,
                )
                first_known_disparity = retained_ranks[
                    retained_ranks > actual_mrca_rank,
                ].min(
                    initial=least_num_strata_deposited,
                )
                policy_requirement = (
                    first_known_disparity - last_known_commonality - 1
                )
                assert policy_requirement >= 0
                for which in (
                    instance,
                    impl(spec),
                ):
                    assert (
                        which(
                            policy,
                            num_strata_deposited_a,
                            num_strata_deposited_b,
                            actual_mrca_rank,
                        )
                        == policy_requirement
                    )


@pytest.mark.parametrize(
    "impl",
    fixed_resolution_algo._scry._CalcMrcaUncertaintyAbsExact_.impls,
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
    fixed_resolution_algo._scry._CalcMrcaUncertaintyAbsExact_.impls,
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
                                fixed_resolution_algo._scry._CalcMrcaUncertaintyAbsExact_.impls,
                                iter_ftor_shims(
                                    lambda p: p.CalcMrcaUncertaintyAbsExact,
                                    fixed_resolution_algo._Policy_.impls,
                                ),
                                iter_no_calcrank_ftor_shims(
                                    lambda p: p.CalcMrcaUncertaintyAbsExact,
                                    fixed_resolution_algo._Policy_.impls,
                                ),
                            )
                        }
                    )
                    == 1
                )
