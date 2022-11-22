import itertools as it

import numpy as np
import pytest

from hstrat.hstrat import geom_seq_nth_root_tapered_algo


@pytest.mark.filterwarnings(
    "ignore:Interspersal set to 1, no bound on MRCA rank estimate uncertainty can be guaranteed."
)
@pytest.mark.parametrize(
    "degree",
    [
        pytest.param(1, marks=pytest.mark.heavy_3a),
        2,
        3,
        7,
        9,
        pytest.param(42, marks=pytest.mark.heavy_2a),
        pytest.param(97, marks=pytest.mark.heavy_2a),
        pytest.param(100, marks=pytest.mark.heavy_2a),
    ],
)
@pytest.mark.parametrize(
    "interspersal",
    [
        pytest.param(1, marks=pytest.mark.heavy_3b),
        2,
        5,
    ],
)
@pytest.mark.parametrize(
    "time_sequence",
    [
        pytest.param(
            it.chain(
                range(10**3),
                np.logspace(10, 32, num=50, base=2, dtype="int"),
            ),
            marks=pytest.mark.heavy_3c,
        ),
        (i for i in range(10) for __ in range(2)),
        (10 - i for i in range(10) for __ in range(2)),
        np.random.default_rng(1).integers(
            low=0,
            high=10**2,
            size=10,
        ),
        pytest.param(
            np.random.default_rng(1).integers(
                low=0,
                high=2**16,
                size=10,
            ),
            marks=pytest.mark.heavy_2b,
        ),
    ],
)
def test_policy_consistency(degree, interspersal, time_sequence):
    policy = geom_seq_nth_root_tapered_algo.Policy(degree, interspersal)
    spec = policy.GetSpec()
    instance = geom_seq_nth_root_tapered_algo.CalcMrcaUncertaintyAbsUpperBound(
        spec,
    )
    for num_strata_deposited in time_sequence:
        for actual_mrca_rank in (
            np.random.default_rng(num_strata_deposited,).integers(
                low=0,
                high=num_strata_deposited,
                size=10**2,
            )
            if num_strata_deposited
            else iter(())
        ):
            policy_requirement = policy.CalcMrcaUncertaintyAbsExact(
                num_strata_deposited,
                num_strata_deposited,
                actual_mrca_rank,
            )
            for which in (
                instance,
                geom_seq_nth_root_tapered_algo.CalcMrcaUncertaintyAbsUpperBound(
                    spec
                ),
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


@pytest.mark.filterwarnings(
    "ignore:Interspersal set to 1, no bound on MRCA rank estimate uncertainty can be guaranteed."
)
@pytest.mark.parametrize(
    "degree",
    [
        1,
        2,
        3,
        7,
        9,
        42,
        97,
        100,
    ],
)
@pytest.mark.parametrize(
    "interspersal",
    [
        1,
        2,
        5,
    ],
)
def test_eq(degree, interspersal):
    policy = geom_seq_nth_root_tapered_algo.Policy(degree, interspersal)
    spec = policy.GetSpec()
    instance = geom_seq_nth_root_tapered_algo.CalcMrcaUncertaintyAbsUpperBound(
        spec
    )

    assert instance == instance
    assert (
        instance
        == geom_seq_nth_root_tapered_algo.CalcMrcaUncertaintyAbsUpperBound(
            spec,
        )
    )
    assert instance is not None


@pytest.mark.filterwarnings(
    "ignore:Interspersal set to 1, no bound on MRCA rank estimate uncertainty can be guaranteed."
)
@pytest.mark.parametrize(
    "degree",
    [
        1,
        2,
        3,
        7,
        9,
        42,
        97,
        100,
    ],
)
@pytest.mark.parametrize(
    "interspersal",
    [
        1,
        2,
        5,
    ],
)
def test_negative_index(degree, interspersal):
    policy = geom_seq_nth_root_tapered_algo.Policy(degree, interspersal)
    spec = policy.GetSpec()
    instance = geom_seq_nth_root_tapered_algo.CalcMrcaUncertaintyAbsUpperBound(
        spec
    )

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
