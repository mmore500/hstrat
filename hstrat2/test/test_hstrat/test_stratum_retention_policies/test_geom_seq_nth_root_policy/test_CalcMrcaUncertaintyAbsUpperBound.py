import itertools as it
import numpy as np
import pytest

from hstrat2.hstrat import geom_seq_nth_root_policy


@pytest.mark.parametrize(
    'degree',
    [
        1,
        2,
        3,
        7,
        9,
        42,
        100,
    ],
)
@pytest.mark.parametrize(
    'interspersal',
    [
        1,
        2,
        5,
    ],
)
@pytest.mark.parametrize(
    'time_sequence',
    [
        it.chain(
            range(10**3),
            np.logspace(10, 32, num=50, base=2, dtype='int'),
        ),
        (i for i in range(10) for __ in range(2)),
        (10 - i for i in range(10) for __ in range(2)),
        np.random.default_rng(1).integers(
            low=0,
            high=10**2,
            size=10,
        ),
        np.random.default_rng(1).integers(
            low=0,
            high=2**16,
            size=10,
        ),
    ],
)
def test_policy_consistency(degree, interspersal, time_sequence):
    policy = geom_seq_nth_root_policy.Policy(degree, interspersal)
    spec = policy.GetSpec()
    instance = geom_seq_nth_root_policy.CalcMrcaUncertaintyAbsUpperBound(
        spec,
    )
    for num_strata_deposited in time_sequence:
        for actual_mrca_rank in np.random.default_rng(
            num_strata_deposited,
        ).integers(
            low=0,
            high=num_strata_deposited,
            size=10**2,
        ) if num_strata_deposited else iter(()):
            policy_requirement = policy.CalcMrcaUncertaintyExact(
                num_strata_deposited,
                num_strata_deposited,
                actual_mrca_rank,
            )
            for which in (
                instance,
                geom_seq_nth_root_policy.CalcMrcaUncertaintyAbsUpperBound(spec)
            ):
                assert which(
                    policy,
                    num_strata_deposited,
                    num_strata_deposited,
                    actual_mrca_rank,
                ) >= policy_requirement

@pytest.mark.parametrize(
    'degree',
    [
        1,
        2,
        3,
        7,
        9,
        42,
        100,
    ],
)
@pytest.mark.parametrize(
    'interspersal',
    [
        1,
        2,
        5,
    ],
)
def test_eq(degree, interspersal):
    policy = geom_seq_nth_root_policy.Policy(degree, interspersal)
    spec = policy.GetSpec()
    instance = geom_seq_nth_root_policy.CalcMrcaUncertaintyAbsUpperBound(spec)

    assert instance == instance
    assert instance == geom_seq_nth_root_policy.CalcMrcaUncertaintyAbsUpperBound(
        spec,
    )
    assert not instance == None
