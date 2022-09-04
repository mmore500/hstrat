import itertools as it

import pytest

from hstrat._auxiliary_lib import all_same
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
def test_impl_consistency(hash_salt):
    policy = pseudostochastic_algo.Policy(hash_salt)
    spec = policy.GetSpec()
    impls = [*pseudostochastic_algo._GenDropRanks_impls]
    instances = [impl(spec) for impl in impls]
    column = HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
    )
    for num_strata_deposited in range(1, 10**3):
        assert all_same(
            it.chain(
                (
                    sorted(
                        impl(spec)(
                            policy,
                            num_strata_deposited,
                            column.IterRetainedRanks(),
                        )
                    )
                    for impl in impls
                ),
                (
                    sorted(
                        instance(
                            policy,
                            num_strata_deposited,
                            column.IterRetainedRanks(),
                        )
                    )
                    for instance in instances
                ),
            )
        )
        column.DepositStratum()


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
    instance = pseudostochastic_algo.GenDropRanks(spec)

    assert instance == instance
    assert instance == pseudostochastic_algo.GenDropRanks(spec)
    assert instance is not None
