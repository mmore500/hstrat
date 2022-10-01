import pickle
import tempfile

import pytest

from hstrat.hstrat import geom_seq_nth_root_algo


@pytest.mark.parametrize(
    "impl",
    geom_seq_nth_root_algo._Policy_.impls,
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
def test_init(impl, degree, interspersal):
    spec = impl(degree, interspersal).GetSpec()
    assert (
        spec
        == impl(
            policy_spec=geom_seq_nth_root_algo.PolicySpec(
                degree, interspersal
            ),
        ).GetSpec()
    )
    assert spec == impl(policy_spec=spec).GetSpec()

    policy = impl(degree, interspersal)

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


@pytest.mark.parametrize(
    "impl",
    geom_seq_nth_root_algo._Policy_.impls,
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
def test_eq(impl, degree, interspersal):
    policy = impl(degree, interspersal)
    assert policy == policy
    assert policy == impl(degree, interspersal)
    assert not policy == policy.WithoutCalcRankAtColumnIndex()
    assert (
        policy.WithoutCalcRankAtColumnIndex()
        == policy.WithoutCalcRankAtColumnIndex()
    )
    assert not policy == impl(degree, interspersal + 1)
    assert not policy == impl(degree + 1, interspersal)
    assert not policy == impl(degree + 1, interspersal + 1)


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


@pytest.mark.parametrize(
    "impl",
    geom_seq_nth_root_algo._Policy_.impls,
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
def test_GetSpec(impl, degree, interspersal):
    spec = impl(degree, interspersal).GetSpec()
    assert spec == type(spec)(degree, interspersal)


@pytest.mark.parametrize(
    "impl",
    geom_seq_nth_root_algo._Policy_.impls,
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
def test_WithoutCalcRankAtColumnIndex(impl, degree, interspersal):

    original = impl(degree, interspersal)
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
        impl(
            degree,
            interspersal,
        ).WithoutCalcRankAtColumnIndex()
        == stripped
    )


@pytest.mark.parametrize(
    "impl",
    geom_seq_nth_root_algo._Policy_.impls,
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
def test_repr(impl, degree, interspersal):
    policy = impl(degree, interspersal)
    assert str(degree) in repr(policy)
    assert str(interspersal) in repr(policy)
    assert policy.GetSpec().GetAlgoIdentifier() in repr(policy)


@pytest.mark.parametrize(
    "impl",
    geom_seq_nth_root_algo._Policy_.impls,
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
def test_str(impl, degree, interspersal):
    policy = impl(degree, interspersal)
    assert str(degree) in str(policy)
    assert str(interspersal) in str(policy)
    assert policy.GetSpec().GetAlgoTitle() in str(policy)


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
@pytest.mark.parametrize(
    "what",
    [
        lambda x: str(x),
    ],
)
def test_consistency(degree, interspersal, what):
    assert (
        len(
            {
                what(impl(degree, interspersal))
                for impl in geom_seq_nth_root_algo._Policy_.impls
            }
        )
        == 1
    )
