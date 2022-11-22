import pytest

from hstrat.hstrat import HereditaryStratigraphicColumn, pseudostochastic_algo


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
def test_policy_consistency(hash_salt):
    policy = pseudostochastic_algo.Policy(hash_salt)
    spec = policy.GetSpec()
    instance = pseudostochastic_algo.CalcNumStrataRetainedUpperBound(spec)
    column = HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
    )
    for num_strata_deposited in range(1, 10**3):
        policy_requirement = column.GetNumStrataRetained()
        for which in (
            instance,
            pseudostochastic_algo.CalcNumStrataRetainedUpperBound(spec),
        ):
            assert (
                which(
                    policy,
                    num_strata_deposited,
                )
                >= policy_requirement
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
def test_eq(hash_salt):
    policy = pseudostochastic_algo.Policy(hash_salt)
    spec = policy.GetSpec()
    instance = pseudostochastic_algo.CalcNumStrataRetainedUpperBound(spec)

    assert instance == instance
    assert instance == pseudostochastic_algo.CalcNumStrataRetainedUpperBound(
        spec,
    )
    assert instance is not None
