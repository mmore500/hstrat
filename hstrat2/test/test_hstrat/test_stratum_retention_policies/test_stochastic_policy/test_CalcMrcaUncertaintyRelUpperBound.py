import itertools as it
import operator
import random

import numpy as np
import pytest

from hstrat2.helpers import find_bounds
from hstrat2.hstrat import (
    HereditaryStratigraphicColumn,
    HereditaryStratumOrderedStoreDict,
    stochastic_policy,
)


@pytest.mark.parametrize(
    "replicate",
    range(5),
)
def test_policy_consistency(replicate):
    random.seed(replicate)
    policy = stochastic_policy.Policy()
    column = HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
        stratum_ordered_store_factory=HereditaryStratumOrderedStoreDict,
    )
    spec = policy.GetSpec()
    instance = stochastic_policy.CalcMrcaUncertaintyRelUpperBound(spec)
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
                stochastic_policy.CalcMrcaUncertaintyRelUpperBound(spec),
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
    "replicate",
    range(5),
)
def test_eq(replicate):
    random.seed(replicate)
    policy = stochastic_policy.Policy()
    spec = policy.GetSpec()
    instance = stochastic_policy.CalcMrcaUncertaintyRelUpperBound(spec)

    assert instance == instance
    assert instance == stochastic_policy.CalcMrcaUncertaintyRelUpperBound(
        spec,
    )
    assert not instance == None


@pytest.mark.parametrize(
    "replicate",
    range(5),
)
def test_negative_index(replicate):
    random.seed(replicate)
    policy = stochastic_policy.Policy()
    spec = policy.GetSpec()
    instance = stochastic_policy.CalcMrcaUncertaintyRelUpperBound(spec)

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
