import itertools as it

import pytest

from hstrat._auxiliary_lib import all_same
from hstrat.hstrat import HereditaryStratigraphicColumn, pseudostochastic_algo


@pytest.mark.parametrize(
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_impl_consistency(fixed_resolution):
    policy = pseudostochastic_algo.Policy(fixed_resolution)
    spec = policy.GetSpec()
    impls = [*pseudostochastic_algo.GenDropRanks_impls]
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
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_eq(fixed_resolution):
    policy = pseudostochastic_algo.Policy(fixed_resolution)
    spec = policy.GetSpec()
    instance = pseudostochastic_algo.GenDropRanks(spec)

    assert instance == instance
    assert instance == pseudostochastic_algo.GenDropRanks(spec)
    assert instance is not None
