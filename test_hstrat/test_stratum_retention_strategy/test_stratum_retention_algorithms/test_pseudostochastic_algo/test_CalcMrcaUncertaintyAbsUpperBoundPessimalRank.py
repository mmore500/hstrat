import numpy as np
import pytest

from hstrat.hstrat import pseudostochastic_algo
from hstrat.stratum_retention_strategy.stratum_retention_algorithms._impl import (
    CalcMrcaUncertaintyAbsUpperBoundPessimalRankBruteForce,
)


@pytest.mark.parametrize(
    "hash_salt",
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
        np.random.default_rng(1).integers(
            10**3,
            size=10**2,
        ),
    ],
)
def test_policy_consistency(hash_salt, time_sequence):
    policy = pseudostochastic_algo.Policy(hash_salt)
    spec = policy.GetSpec()
    instance = (
        pseudostochastic_algo.CalcMrcaUncertaintyAbsUpperBoundPessimalRank(
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
                    pseudostochastic_algo.CalcMrcaUncertaintyAbsUpperBoundPessimalRank(
                        spec
                    ),
                ):
                    assert (
                        policy.CalcMrcaUncertaintyAbsUpperBound(
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
    "hash_salt",
    [
        1,
        2,
        3,
        7,
    ],
)
def test_eq(hash_salt):
    policy = pseudostochastic_algo.Policy(hash_salt)
    spec = policy.GetSpec()
    instance = (
        pseudostochastic_algo.CalcMrcaUncertaintyAbsUpperBoundPessimalRank(
            spec
        )
    )

    assert instance == instance
    assert (
        instance
        == pseudostochastic_algo.CalcMrcaUncertaintyAbsUpperBoundPessimalRank(
            spec,
        )
    )
    assert instance is not None
