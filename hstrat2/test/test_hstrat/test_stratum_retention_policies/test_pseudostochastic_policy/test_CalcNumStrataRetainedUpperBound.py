import pytest

from hstrat2.hstrat import (
    HereditaryStratigraphicColumn,
    pseudostochastic_policy,
)


@pytest.mark.parametrize(
    "random_seed",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_policy_consistency(random_seed):
    policy = pseudostochastic_policy.Policy(random_seed)
    spec = policy.GetSpec()
    instance = pseudostochastic_policy.CalcNumStrataRetainedUpperBound(spec)
    column = HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
    )
    for num_strata_deposited in range(1, 10**3):
        policy_requirement = column.GetNumStrataRetained()
        for which in (
            instance,
            pseudostochastic_policy.CalcNumStrataRetainedUpperBound(spec),
        ):
            assert (
                which(
                    policy,
                    num_strata_deposited,
                )
                >= policy_requirement
            )


@pytest.mark.parametrize(
    "random_seed",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_eq(random_seed):
    policy = pseudostochastic_policy.Policy(random_seed)
    spec = policy.GetSpec()
    instance = pseudostochastic_policy.CalcNumStrataRetainedUpperBound(spec)

    assert instance == instance
    assert instance == pseudostochastic_policy.CalcNumStrataRetainedUpperBound(
        spec,
    )
    assert instance is not None
