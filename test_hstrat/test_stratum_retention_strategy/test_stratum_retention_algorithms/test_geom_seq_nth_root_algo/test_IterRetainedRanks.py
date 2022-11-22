import itertools as it
import numbers

from iterpop import iterpop as ip
import numpy as np
import pytest

from hstrat._auxiliary_lib import pairwise
from hstrat.hstrat import geom_seq_nth_root_algo


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
                range(10**4),
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
                high=2**32,
                size=10,
            ),
            marks=pytest.mark.heavy_2b,
        ),
    ],
)
def test_only_dwindling_over_time(degree, interspersal, time_sequence):
    policy = geom_seq_nth_root_algo.Policy(degree, interspersal)
    spec = policy.GetSpec()
    instance = geom_seq_nth_root_algo.IterRetainedRanks(spec)
    for num_strata_deposited in time_sequence:
        for which in (
            instance,
            geom_seq_nth_root_algo.IterRetainedRanks(spec),
        ):
            cur_set = {
                *which(
                    policy,
                    num_strata_deposited,
                )
            }
            next_set = {
                *which(
                    policy,
                    num_strata_deposited + 1,
                )
            }
            assert cur_set.issuperset(next_set - {num_strata_deposited})


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
                range(10**4),
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
                high=2**32,
                size=10,
            ),
            marks=pytest.mark.heavy_2b,
        ),
    ],
)
def test_ranks_sorted_and_unique(degree, interspersal, time_sequence):
    policy = geom_seq_nth_root_algo.Policy(degree, interspersal)
    spec = policy.GetSpec()
    instance = geom_seq_nth_root_algo.IterRetainedRanks(spec)
    for num_strata_deposited in time_sequence:
        for which in (
            instance,
            geom_seq_nth_root_algo.IterRetainedRanks(spec),
        ):
            assert all(
                i < j
                for i, j in pairwise(
                    which(
                        policy,
                        num_strata_deposited,
                    )
                )
            )


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
                range(10**4),
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
                high=2**32,
                size=10,
            ),
            marks=pytest.mark.heavy_2b,
        ),
    ],
)
def test_zero_and_last_ranks_retained(degree, interspersal, time_sequence):
    policy = geom_seq_nth_root_algo.Policy(degree, interspersal)
    spec = policy.GetSpec()
    instance = geom_seq_nth_root_algo.IterRetainedRanks(spec)
    for num_strata_deposited in time_sequence:
        for which in (
            instance,
            geom_seq_nth_root_algo.IterRetainedRanks(spec),
        ):
            res = which(
                policy,
                num_strata_deposited,
            )
            if num_strata_deposited > 1:
                first, *middle, last = res
                assert first == 0
                assert last == num_strata_deposited - 1
            elif num_strata_deposited == 1:
                assert ip.popsingleton(res) == 0
            else:
                assert next(res, None) is None


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
                range(10**4),
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
                high=2**32,
                size=10,
            ),
            marks=pytest.mark.heavy_2b,
        ),
    ],
)
def test_ranks_valid(degree, interspersal, time_sequence):
    policy = geom_seq_nth_root_algo.Policy(degree, interspersal)
    spec = policy.GetSpec()
    instance = geom_seq_nth_root_algo.IterRetainedRanks(spec)
    for num_strata_deposited in time_sequence:
        for which in (
            instance,
            geom_seq_nth_root_algo.IterRetainedRanks(spec),
        ):
            assert all(
                isinstance(r, numbers.Integral)
                and 0 <= r < num_strata_deposited
                for r in which(policy, num_strata_deposited)
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
    policy = geom_seq_nth_root_algo.Policy(degree, interspersal)
    spec = policy.GetSpec()
    instance = geom_seq_nth_root_algo.IterRetainedRanks(spec)

    assert instance == instance
    assert instance == geom_seq_nth_root_algo.IterRetainedRanks(spec)
    assert instance is not None
