import itertools as it
import operator

import pytest

from hstrat._auxiliary_lib import find_bounds
from hstrat.hstrat import (
    HereditaryStratigraphicColumn,
    HereditaryStratumOrderedStoreDict,
    pseudostochastic_algo,
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
def test_policy_consistency(hash_salt):
    policy = pseudostochastic_algo.Policy(hash_salt)
    column = HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
        stratum_ordered_store=HereditaryStratumOrderedStoreDict,
    )
    spec = policy.GetSpec()
    instance = pseudostochastic_algo.CalcMrcaUncertaintyRelUpperBound(spec)
    for num_strata_deposited in range(1, 200):
        for actual_mrca_rank in it.chain(
            range(min(100, num_strata_deposited)),
            range(100, num_strata_deposited, 47),
        ):
            recency = max(
                num_strata_deposited - 1 - actual_mrca_rank,
                1,
            )
            lb, ub = find_bounds(
                query=actual_mrca_rank,
                iterable=column.IterRetainedRanks(),
                initializer=(0, num_strata_deposited - 1),
                filter_above=operator.ge,
                filter_below=operator.le,
            )
            policy_requirement = (ub - lb) / recency
            for which in (
                instance,
                pseudostochastic_algo.CalcMrcaUncertaintyRelUpperBound(spec),
            ):
                assert (
                    which(
                        policy,
                        num_strata_deposited,
                        num_strata_deposited,
                        actual_mrca_rank,
                    )
                    >= policy_requirement
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
    instance = pseudostochastic_algo.CalcMrcaUncertaintyRelUpperBound(spec)

    assert instance == instance
    assert instance == pseudostochastic_algo.CalcMrcaUncertaintyRelUpperBound(
        spec,
    )
    assert instance is not None


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
def test_negative_index(hash_salt):
    policy = pseudostochastic_algo.Policy(hash_salt)
    spec = policy.GetSpec()
    instance = pseudostochastic_algo.CalcMrcaUncertaintyRelUpperBound(spec)

    for diff in range(1, 100):
        assert instance(policy, 100, 100, -diff,) == instance(
            policy,
            100,
            100,
            99 - diff,
        )

        assert instance(policy, 101, 100, -diff,) == instance(
            policy,
            101,
            100,
            99 - diff,
        )

        assert instance(policy, 150, 100, -diff,) == instance(
            policy,
            150,
            100,
            99 - diff,
        )

        assert instance(policy, 100, 101, -diff,) == instance(
            policy,
            101,
            100,
            99 - diff,
        )

        assert instance(policy, 100, 150, -diff,) == instance(
            policy,
            150,
            100,
            99 - diff,
        )
