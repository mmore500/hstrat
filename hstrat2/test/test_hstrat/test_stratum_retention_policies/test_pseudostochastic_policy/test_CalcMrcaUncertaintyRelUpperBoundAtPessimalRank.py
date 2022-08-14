import numpy as np
import pytest

from hstrat2.hstrat import pseudostochastic_policy
from hstrat2.hstrat.stratum_retention_policies._detail \
    import CalcMrcaUncertaintyRelUpperBoundPessimalRankBruteForce


@pytest.mark.parametrize(
    'random_seed',
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
    'time_sequence',
    [
        range(10**2),
        np.random.default_rng(1).integers(
            10**3,
            size=10**2,
        )
    ],
)
def test_policy_consistency(random_seed, time_sequence):
    policy = pseudostochastic_policy.Policy(random_seed)
    spec = policy.GetSpec()
    instance = pseudostochastic_policy.CalcMrcaUncertaintyRelUpperBoundAtPessimalRank(
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
                    pseudostochastic_policy.CalcMrcaUncertaintyRelUpperBoundAtPessimalRank(spec)
                ):
                    assert which(
                        policy,
                        num_strata_deposited_a,
                        num_strata_deposited_b,
                    ) == policy_requirement

@pytest.mark.parametrize(
    'random_seed',
    [
        1,
        2,
        3,
        7,
    ],
)
def test_eq(random_seed):
    policy = pseudostochastic_policy.Policy(random_seed)
    spec = policy.GetSpec()
    instance = pseudostochastic_policy.CalcMrcaUncertaintyRelUpperBoundAtPessimalRank(spec)

    assert instance == instance
    assert instance == pseudostochastic_policy.CalcMrcaUncertaintyRelUpperBoundAtPessimalRank(
        spec,
    )
    assert not instance == None
