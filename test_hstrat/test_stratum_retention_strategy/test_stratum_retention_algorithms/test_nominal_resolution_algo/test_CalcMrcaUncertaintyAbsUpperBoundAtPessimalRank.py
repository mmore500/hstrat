import numpy as np
import pytest

from hstrat.hstrat import nominal_resolution_algo
from hstrat.stratum_retention_strategy.stratum_retention_algorithms._impl import (
    CalcMrcaUncertaintyAbsUpperBoundPessimalRankBruteForce,
)


@pytest.mark.parametrize(
    "time_sequence",
    [
        range(10**2),
        np.random.default_rng(1).integers(
            10**3,
            size=10**2,
        ),
    ],
)
def test_policy_consistency(time_sequence):
    policy = nominal_resolution_algo.Policy()
    spec = policy.GetSpec()
    instance = (
        nominal_resolution_algo.CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank(
            spec,
        )
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
                policy_requirement = policy.CalcMrcaUncertaintyAbsUpperBound(
                    num_strata_deposited_a,
                    num_strata_deposited_b,
                    CalcMrcaUncertaintyAbsUpperBoundPessimalRankBruteForce()(
                        policy,
                        num_strata_deposited_a,
                        num_strata_deposited_b,
                    ),
                )
                for which in (
                    instance,
                    nominal_resolution_algo.CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank(
                        spec
                    ),
                ):
                    assert (
                        which(
                            policy,
                            num_strata_deposited_a,
                            num_strata_deposited_b,
                        )
                        == policy_requirement
                    )


def test_eq():
    policy = nominal_resolution_algo.Policy()
    spec = policy.GetSpec()
    instance = (
        nominal_resolution_algo.CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank(
            spec
        )
    )

    assert instance == instance
    assert (
        instance
        == nominal_resolution_algo.CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank(
            spec,
        )
    )
    assert instance is not None
