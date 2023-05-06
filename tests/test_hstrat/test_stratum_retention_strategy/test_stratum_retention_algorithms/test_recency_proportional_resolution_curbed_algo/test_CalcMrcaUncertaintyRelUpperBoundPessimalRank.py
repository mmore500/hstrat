import numpy as np
import pytest

from hstrat.hstrat import recency_proportional_resolution_curbed_algo
from hstrat.stratum_retention_strategy.stratum_retention_algorithms._impl import (
    CalcMrcaUncertaintyRelUpperBoundPessimalRankBruteForce,
)


@pytest.mark.parametrize(
    "size_curb",
    [
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
def test_policy_consistency(size_curb, time_sequence):
    policy = recency_proportional_resolution_curbed_algo.Policy(size_curb)
    spec = policy.GetSpec()
    instance = recency_proportional_resolution_curbed_algo.CalcMrcaUncertaintyRelUpperBoundPessimalRank(
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
                recency_proportional_resolution_curbed_algo.CalcMrcaUncertaintyRelUpperBoundPessimalRank(
                    spec
                ),
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
    "size_curb",
    [
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_eq(size_curb):
    policy = recency_proportional_resolution_curbed_algo.Policy(size_curb)
    spec = policy.GetSpec()
    instance = recency_proportional_resolution_curbed_algo.CalcMrcaUncertaintyRelUpperBoundPessimalRank(
        spec
    )

    assert instance == instance
    assert (
        instance
        == recency_proportional_resolution_curbed_algo.CalcMrcaUncertaintyRelUpperBoundPessimalRank(
            spec,
        )
    )
    assert instance is not None
