import itertools as it

import numpy as np
import pytest

from hstrat._auxiliary_lib import all_same
from hstrat.hstrat import nominal_resolution_algo


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
def test_impl_consistency(time_sequence):
    policy = nominal_resolution_algo.Policy()
    spec = policy.GetSpec()
    impls = [*nominal_resolution_algo._GenDropRanks_impls]
    instances = [impl(spec) for impl in impls]
    for num_strata_deposited in time_sequence:
        assert all_same(
            it.chain(
                (
                    sorted(
                        impl(spec)(
                            policy,
                            num_strata_deposited,
                            policy.IterRetainedRanks(num_strata_deposited),
                        )
                    )
                    for impl in impls
                ),
                (
                    sorted(
                        instance(
                            policy,
                            num_strata_deposited,
                            policy.IterRetainedRanks(num_strata_deposited),
                        )
                    )
                    for instance in instances
                ),
            )
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
def test_policy_consistency(time_sequence):
    policy = nominal_resolution_algo.Policy()
    spec = policy.GetSpec()
    instance = nominal_resolution_algo.GenDropRanks(spec)
    for num_strata_deposited in time_sequence:
        policy_requirement = {
            *policy.IterRetainedRanks(
                num_strata_deposited,
            )
        } - {
            *policy.IterRetainedRanks(
                num_strata_deposited + 1,
            )
        }
        for which in (
            instance,
            nominal_resolution_algo.GenDropRanks(spec),
        ):
            assert sorted(
                which(
                    policy,
                    num_strata_deposited,
                    policy.IterRetainedRanks(num_strata_deposited),
                )
            ) == sorted(policy_requirement)


def test_eq():
    policy = nominal_resolution_algo.Policy()
    spec = policy.GetSpec()
    instance = nominal_resolution_algo.GenDropRanks(spec)

    assert instance == instance
    assert instance == nominal_resolution_algo.GenDropRanks(spec)
    assert instance is not None
