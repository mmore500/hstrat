import pickle
import tempfile

import pytest

from hstrat.hstrat import geom_seq_nth_root_algo


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
def test_init(degree, interspersal):
    assert (
        geom_seq_nth_root_algo.Policy(degree, interspersal).GetSpec()
        == geom_seq_nth_root_algo.Policy(
            policy_spec=geom_seq_nth_root_algo.PolicySpec(
                degree, interspersal
            ),
        ).GetSpec()
    )

    policy = geom_seq_nth_root_algo.Policy(degree, interspersal)

    # invariants
    assert callable(policy.CalcMrcaUncertaintyAbsUpperBound)
    assert callable(policy.CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank)
    assert callable(policy.CalcMrcaUncertaintyAbsUpperBoundPessimalRank)
    assert callable(policy.CalcMrcaUncertaintyRelUpperBound)
    assert callable(policy.CalcMrcaUncertaintyRelUpperBoundAtPessimalRank)
    assert callable(policy.CalcMrcaUncertaintyRelUpperBoundPessimalRank)
    assert callable(policy.CalcNumStrataRetainedUpperBound)
    # scrying
    assert callable(policy.CalcMrcaUncertaintyAbsExact)
    assert callable(policy.CalcMrcaUncertaintyRelExact)
    assert callable(policy.CalcNumStrataRetainedExact)
    assert callable(policy.CalcRankAtColumnIndex)
    assert callable(policy.IterRetainedRanks)
    # enactment
    assert callable(policy.GenDropRanks)


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
    assert policy == policy
    assert policy == geom_seq_nth_root_algo.Policy(degree, interspersal)
    assert not policy == policy.WithoutCalcRankAtColumnIndex()
    assert (
        policy.WithoutCalcRankAtColumnIndex()
        == policy.WithoutCalcRankAtColumnIndex()
    )
    assert not policy == geom_seq_nth_root_algo.Policy(
        degree, interspersal + 1
    )
    assert not policy == geom_seq_nth_root_algo.Policy(
        degree + 1, interspersal
    )
    assert not policy == geom_seq_nth_root_algo.Policy(
        degree + 1, interspersal + 1
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
def test_pickle(degree, interspersal):
    original = geom_seq_nth_root_algo.Policy(degree, interspersal)
    with tempfile.TemporaryDirectory() as tmp_path:
        with open(f"{tmp_path}/data", "wb") as tmp_file:
            pickle.dump(original, tmp_file)

        with open(f"{tmp_path}/data", "rb") as tmp_file:
            reconstituted = pickle.load(tmp_file)
            assert reconstituted == original


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
def test_GetSpec(degree, interspersal):
    assert geom_seq_nth_root_algo.Policy(
        degree, interspersal
    ).GetSpec() == geom_seq_nth_root_algo.PolicySpec(degree, interspersal)


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
def test_WithoutCalcRankAtColumnIndex(degree, interspersal):

    original = geom_seq_nth_root_algo.Policy(degree, interspersal)
    stripped = original.WithoutCalcRankAtColumnIndex()

    assert stripped.CalcRankAtColumnIndex is None

    assert (
        original.CalcMrcaUncertaintyAbsUpperBound
        == stripped.CalcMrcaUncertaintyAbsUpperBound
    )
    assert (
        original.CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank
        == stripped.CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank
    )
    assert (
        original.CalcMrcaUncertaintyAbsUpperBoundPessimalRank
        == stripped.CalcMrcaUncertaintyAbsUpperBoundPessimalRank
    )
    assert (
        original.CalcMrcaUncertaintyRelUpperBound
        == stripped.CalcMrcaUncertaintyRelUpperBound
    )
    assert (
        original.CalcMrcaUncertaintyRelUpperBoundAtPessimalRank
        == stripped.CalcMrcaUncertaintyRelUpperBoundAtPessimalRank
    )
    assert (
        original.CalcMrcaUncertaintyRelUpperBoundPessimalRank
        == stripped.CalcMrcaUncertaintyRelUpperBoundPessimalRank
    )
    assert (
        original.CalcNumStrataRetainedUpperBound
        == stripped.CalcNumStrataRetainedUpperBound
    )
    # scrying
    assert (
        original.CalcMrcaUncertaintyAbsExact
        == stripped.CalcMrcaUncertaintyAbsExact
    )
    assert (
        original.CalcMrcaUncertaintyRelExact
        == stripped.CalcMrcaUncertaintyRelExact
    )
    assert (
        original.CalcNumStrataRetainedExact
        == stripped.CalcNumStrataRetainedExact
    )
    assert original.IterRetainedRanks == stripped.IterRetainedRanks
    # enactment
    assert original.GenDropRanks == stripped.GenDropRanks

    # test chaining
    assert (
        geom_seq_nth_root_algo.Policy(
            degree,
            interspersal,
        ).WithoutCalcRankAtColumnIndex()
        == stripped
    )


def test_repr():
    degree = 1
    interspersal = 2
    policy = geom_seq_nth_root_algo.Policy(degree, interspersal)
    assert str(degree) in repr(policy)
    assert str(interspersal) in repr(policy)
    assert policy.GetSpec().GetAlgoIdentifier() in repr(policy)


def test_str():
    degree = 1
    interspersal = 2
    policy = geom_seq_nth_root_algo.Policy(degree, interspersal)
    assert str(degree) in str(policy)
    assert str(interspersal) in str(policy)
    assert policy.GetSpec().GetAlgoTitle() in str(policy)
