import random

import pytest

from hstrat.hstrat import HereditaryStratigraphicColumn, stochastic_algo


@pytest.mark.parametrize(
    "replicate",
    range(5),
)
def test_policy_consistency(replicate):
    random.seed(replicate)
    policy = stochastic_algo.Policy()
    spec = policy.GetSpec()
    instance = stochastic_algo.CalcNumStrataRetainedUpperBound(spec)
    column = HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
    )
    for num_strata_deposited in range(1, 10**3):
        policy_requirement = column.GetNumStrataRetained()
        for which in (
            instance,
            stochastic_algo.CalcNumStrataRetainedUpperBound(spec),
        ):
            assert (
                which(
                    policy,
                    num_strata_deposited,
                )
                >= policy_requirement
            )


@pytest.mark.parametrize(
    "replicate",
    range(5),
)
def test_eq(replicate):
    random.seed(replicate)
    policy = stochastic_algo.Policy()
    spec = policy.GetSpec()
    instance = stochastic_algo.CalcNumStrataRetainedUpperBound(spec)

    assert instance == instance
    assert instance == stochastic_algo.CalcNumStrataRetainedUpperBound(
        spec,
    )
    assert instance is not None
