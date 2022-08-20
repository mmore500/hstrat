import itertools as it
import random

import pytest

from hstrat2.helpers import all_same
from hstrat2.hstrat import HereditaryStratigraphicColumn, stochastic_policy


@pytest.mark.parametrize(
    "impl",
    stochastic_policy.GenDropRanks_impls,
)
@pytest.mark.parametrize(
    "replicate",
    range(5),
)
def test_impl_stochasticity(impl, replicate):
    random.seed(replicate)
    policy = stochastic_policy.Policy()
    spec = policy.GetSpec()
    column = HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
    )
    for num_strata_deposited in range(1, 10**3):
        if all_same(
            it.chain(
                (
                    sorted(
                        impl(spec)(
                            policy,
                            num_strata_deposited,
                            column.IterRetainedRanks(),
                        )
                    )
                ),
                (
                    sorted(
                        impl(spec)(
                            policy,
                            num_strata_deposited,
                            column.IterRetainedRanks(),
                        )
                    )
                ),
            )
        ):
            break
        else:
            assert False, "All implementations were identical."


@pytest.mark.parametrize(
    "replicate",
    range(5),
)
def test_eq(replicate):
    random.seed(replicate)
    policy = stochastic_policy.Policy()
    spec = policy.GetSpec()
    instance = stochastic_policy.GenDropRanks(spec)

    assert instance == instance
    assert instance == stochastic_policy.GenDropRanks(spec)
    assert instance is not None
