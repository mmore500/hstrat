import itertools as it
import operator
import numpy as np
import pytest

from hstrat2.helpers import find_bounds
from hstrat2.hstrat import HereditaryStratigraphicColumn
from hstrat2.hstrat import HereditaryStratumOrderedStoreDict
from hstrat2.hstrat import pseudostochastic_policy


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
def test_policy_consistency(random_seed):
    policy = pseudostochastic_policy.Policy(random_seed)
    column = HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
        stratum_ordered_store_factory=HereditaryStratumOrderedStoreDict,

    )
    spec = policy.GetSpec()
    instance = pseudostochastic_policy.CalcMrcaUncertaintyAbsUpperBound(spec)
    for num_strata_deposited in range(1, 200):
        for actual_mrca_rank in it.chain(
            range(min(100, num_strata_deposited)),
            range(100, num_strata_deposited, 47),
        ):
            lb, ub = find_bounds(
                query=actual_mrca_rank,
                iterable=column.IterRetainedRanks(),
                initializer=(0, num_strata_deposited - 1),
                filter_above=operator.ge,
                filter_below=operator.le,
            )
            policy_requirement = ub - lb
            for which in (
                instance,
                pseudostochastic_policy.CalcMrcaUncertaintyAbsUpperBound(spec)
            ):
                assert which(
                    policy,
                    num_strata_deposited,
                    actual_mrca_rank,
                ) >= policy_requirement
        column.DepositStratum()

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
def test_eq(random_seed):
    policy = pseudostochastic_policy.Policy(random_seed)
    spec = policy.GetSpec()
    instance = pseudostochastic_policy.CalcMrcaUncertaintyAbsUpperBound(spec)

    assert instance == instance
    assert instance == pseudostochastic_policy.CalcMrcaUncertaintyAbsUpperBound(
        spec,
    )
    assert not instance == None
