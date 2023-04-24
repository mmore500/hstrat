import itertools as it

import numpy as np
import pytest

from hstrat._testing import iter_ftor_shims, iter_no_calcrank_ftor_shims
from hstrat.hstrat import recency_proportional_resolution_algo


@pytest.mark.parametrize(
    "impl",
    recency_proportional_resolution_algo._scry._CalcNumStrataRetainedExact_.impls,
)
@pytest.mark.parametrize(
    "recency_proportional_resolution",
    [
        0,
        1,
        2,
        3,
        7,
        42,
        97,
        100,
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
def test_policy_consistency(
    impl, recency_proportional_resolution, time_sequence
):
    policy = recency_proportional_resolution_algo.Policy(
        recency_proportional_resolution
    )
    spec = policy.GetSpec()
    instance = impl(spec)
    for num_strata_deposited in time_sequence:
        policy_requirement = len(
            [
                *policy.IterRetainedRanks(
                    num_strata_deposited,
                )
            ]
        )
        for which in (
            instance,
            impl(spec),
        ):
            assert (
                which(
                    policy,
                    num_strata_deposited,
                )
                == policy_requirement
            )


@pytest.mark.parametrize(
    "impl",
    recency_proportional_resolution_algo._scry._CalcNumStrataRetainedExact_.impls,
)
@pytest.mark.parametrize(
    "recency_proportional_resolution",
    [
        0,
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_eq(impl, recency_proportional_resolution):
    policy = recency_proportional_resolution_algo.Policy(
        recency_proportional_resolution
    )
    spec = policy.GetSpec()
    instance = impl(spec)

    assert instance == instance
    assert instance == impl(spec)
    assert instance is not None


@pytest.mark.parametrize(
    "recency_proportional_resolution",
    [
        0,
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
@pytest.mark.parametrize(
    "time_sequence",
    [
        range(10**3),
        np.random.default_rng(1).integers(
            low=0,
            high=2**32,
            size=10,
        ),
        (2**32,),
    ],
)
def test_impl_consistency(recency_proportional_resolution, time_sequence):
    policy = recency_proportional_resolution_algo.Policy(
        recency_proportional_resolution
    )
    spec = policy.GetSpec()

    for gen in time_sequence:
        assert (
            len(
                {
                    impl(spec)(
                        policy,
                        gen,
                    )
                    for impl in it.chain(
                        recency_proportional_resolution_algo._scry._CalcNumStrataRetainedExact_.impls,
                        iter_ftor_shims(
                            lambda p: p.CalcNumStrataRetainedExact,
                            recency_proportional_resolution_algo._Policy_.impls,
                        ),
                        iter_no_calcrank_ftor_shims(
                            lambda p: p.CalcNumStrataRetainedExact,
                            recency_proportional_resolution_algo._Policy_.impls,
                        ),
                    )
                }
            )
            == 1
        )
