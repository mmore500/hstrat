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
    instance = geom_seq_nth_root_tapered_algo.CalcMrcaUncertaintyAbsExact(spec)
    for num_strata_deposited in time_sequence:
        retained_ranks = np.fromiter(
            policy.IterRetainedRanks(num_strata_deposited),
            int,
        )
        for actual_mrca_rank in it.chain(
            range(min(num_strata_deposited, 10**3)),
            np.random.default_rng(1).integers(
                low=0,
                high=num_strata_deposited,
                size=10**2,
            )
            if num_strata_deposited
            else iter(()),
        ):
            last_known_commonality = retained_ranks[
                retained_ranks <= actual_mrca_rank,
            ].max(
                initial=0,
            )
            first_known_disparity = retained_ranks[
                retained_ranks > actual_mrca_rank,
            ].min(
                initial=num_strata_deposited,
            )
            policy_requirement = (
                first_known_disparity - last_known_commonality - 1
            )
            assert policy_requirement >= 0
            for which in (
                instance,
                geom_seq_nth_root_tapered_algo.CalcMrcaUncertaintyAbsExact(
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
                    == policy_requirement
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
        pytest.param(42, marks=pytest.mark.heavy_2a),
        pytest.param(97, marks=pytest.mark.heavy_2a),
        pytest.param(100, marks=pytest.mark.heavy_2a),
    ],
)
@pytest.mark.parametrize(
    "interspersal",
    [
        pytest.param(1, marks=pytest.mark.heavy_2b),
        2,
        5,
    ],
)
def test_policy_consistency_uneven_branches(degree, interspersal):
    policy = geom_seq_nth_root_tapered_algo.Policy(degree, interspersal)
    spec = policy.GetSpec()
    instance = geom_seq_nth_root_tapered_algo.CalcMrcaUncertaintyAbsExact(spec)
    sample_durations = it.chain(
        range(10**2),
        np.logspace(7, 16, num=10, base=2, dtype="int"),
    )
    for num_strata_deposited_a in sample_durations:
        ranks_a = set(policy.IterRetainedRanks(num_strata_deposited_a))
        for num_strata_deposited_b in sample_durations:
            ranks_b = set(policy.IterRetainedRanks(num_strata_deposited_b))
            retained_ranks = np.fromiter(ranks_a & ranks_b, int)
            least_num_strata_deposited = min(
                num_strata_deposited_a,
                num_strata_deposited_b,
            )
            for actual_mrca_rank in range(least_num_strata_deposited):
                last_known_commonality = retained_ranks[
                    retained_ranks <= actual_mrca_rank,
                ].max(
                    initial=0,
                )
                first_known_disparity = retained_ranks[
                    retained_ranks > actual_mrca_rank,
                ].min(
                    initial=least_num_strata_deposited,
                )
                policy_requirement = (
                    first_known_disparity - last_known_commonality - 1
                )
                assert policy_requirement >= 0
                for which in (
                    instance,
                    geom_seq_nth_root_tapered_algo.CalcMrcaUncertaintyAbsExact(
                        spec
                    ),
                ):
                    assert (
                        which(
                            policy,
                            num_strata_deposited_a,
                            num_strata_deposited_b,
                            actual_mrca_rank,
                        )
                        == policy_requirement
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
    instance = geom_seq_nth_root_tapered_algo.CalcMrcaUncertaintyAbsExact(spec)

    assert instance == instance
    assert (
        instance
        == geom_seq_nth_root_tapered_algo.CalcMrcaUncertaintyAbsExact(spec)
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
    instance = geom_seq_nth_root_tapered_algo.CalcMrcaUncertaintyAbsExact(spec)

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
