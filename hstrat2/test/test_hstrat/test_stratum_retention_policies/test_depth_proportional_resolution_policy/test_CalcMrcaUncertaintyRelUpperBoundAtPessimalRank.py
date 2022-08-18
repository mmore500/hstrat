import numpy as np
import pytest

from hstrat2.hstrat import depth_proportional_resolution_policy
from hstrat2.hstrat.stratum_retention_policies._detail import (
    CalcMrcaUncertaintyRelUpperBoundPessimalRankBruteForce,
)


@pytest.mark.parametrize(
    'depth_proportional_resolution',
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
    'time_sequence',
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
def test_policy_consistency(depth_proportional_resolution, time_sequence):
    policy = depth_proportional_resolution_policy.Policy(depth_proportional_resolution)
    spec = policy.GetSpec()
    instance = depth_proportional_resolution_policy.CalcMrcaUncertaintyRelUpperBoundAtPessimalRank(
        spec,
    )
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
                    depth_proportional_resolution_policy.CalcMrcaUncertaintyRelUpperBoundAtPessimalRank(spec),
                ):
                    assert which(
                        policy,
                        num_strata_deposited_a,
                        num_strata_deposited_b,
                    ) == policy_requirement

@pytest.mark.parametrize(
    'depth_proportional_resolution',
    [
        1,
        2,
        3,
        7,
    ],
)
def test_eq(depth_proportional_resolution):
    policy = depth_proportional_resolution_policy.Policy(depth_proportional_resolution)
    spec = policy.GetSpec()
    instance = depth_proportional_resolution_policy.CalcMrcaUncertaintyRelUpperBoundAtPessimalRank(spec)

    assert instance == instance
    assert instance == depth_proportional_resolution_policy.CalcMrcaUncertaintyRelUpperBoundAtPessimalRank(
        spec,
    )
    assert not instance == None
