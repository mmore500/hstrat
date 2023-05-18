import itertools as it

import numpy as np
import pytest

from hstrat._auxiliary_lib import all_same
from hstrat.hstrat import recency_proportional_resolution_curbed_algo


@pytest.mark.parametrize(
    "size_curb",
    [
        2,
        3,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        42,
        97,
        100,
        254,
        255,
        256,
        257,
    ],
)
@pytest.mark.parametrize(
    "time_sequence",
    [
        range(10**3),
        (i for i in range(10**2) for __ in range(2)),
        np.random.default_rng(1).integers(
            low=0,
            high=2**32,
            size=10,
        ),
        (2**32,),
    ],
)
def test_impl_consistency(size_curb, time_sequence):
    policy = recency_proportional_resolution_curbed_algo.Policy(size_curb)
    spec = policy.GetSpec()
    impls = [*recency_proportional_resolution_curbed_algo._GenDropRanks_impls]
    instances = [impl(spec) for impl in impls]
    for num_strata_deposited in time_sequence:
        assert all_same(
            it.chain(
                (
                    sorted(
                        impl(spec)(
                            policy,
                            num_strata_deposited,
                            policy.IterRetainedRanks(num_strata_deposited),
                        )
                    )
                    for impl in impls
                ),
                (
                    sorted(
                        instance(
                            policy,
                            num_strata_deposited,
                            policy.IterRetainedRanks(num_strata_deposited),
                        )
                    )
                    for instance in instances
                ),
            )
        )
