import itertools as it
import operator
import numpy as np
import pytest
import random

from hstrat2.helpers import find_bounds
from hstrat2.hstrat import HereditaryStratigraphicColumn
from hstrat2.hstrat import HereditaryStratumOrderedStoreDict
from hstrat2.hstrat import stochastic_policy


@pytest.mark.parametrize(
    'replicate',
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
    instance = stochastic_policy.CalcMrcaUncertaintyUpperBound(spec)
    for num_strata_deposited in range(1, 200):
        for actual_mrca_rank in it.chain(
            range(min(100, num_strata_deposited)),
            range(100, num_strata_deposited, 47),
        ):
            lb, ub = find_bounds(
                query=actual_mrca_rank,
                iterable=column.GetRetainedRanks(),
                initializer=(0, num_strata_deposited - 1),
                filter_above=operator.ge,
                filter_below=operator.le,
            )
            policy_requirement = ub - lb
            for which in (
                instance,
                stochastic_policy.CalcMrcaUncertaintyUpperBound(spec)
            ):
                assert which(
                    policy,
                    num_strata_deposited,
                    actual_mrca_rank,
                ) >= policy_requirement
        column.DepositStratum()

@pytest.mark.parametrize(
    'replicate',
    range(5),
)
def test_eq(replicate):
    random.seed(replicate)
    policy = stochastic_policy.Policy()
    spec = policy.GetSpec()
    instance = stochastic_policy.CalcMrcaUncertaintyUpperBound(spec)

    assert instance == instance
    assert instance == stochastic_policy.CalcMrcaUncertaintyUpperBound(
        spec,
    )
    assert not instance == None
