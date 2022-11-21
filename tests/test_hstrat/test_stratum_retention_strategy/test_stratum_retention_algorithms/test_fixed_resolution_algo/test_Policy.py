import pickle
import tempfile

import pytest

from hstrat.hstrat import fixed_resolution_algo


@pytest.mark.parametrize(
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_init(fixed_resolution):
    assert (
        fixed_resolution_algo.Policy(fixed_resolution).GetSpec()
        == fixed_resolution_algo.Policy(
            policy_spec=fixed_resolution_algo.PolicySpec(fixed_resolution),
        ).GetSpec()
    )

    policy = fixed_resolution_algo.Policy(fixed_resolution)

    # invariants
    assert callable(policy.CalcMrcaUncertaintyAbsUpperBound)
    assert callable(policy.CalcMrcaUncertaintyAbsUpperBoundPessimalRank)
    assert callable(policy.CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank)
    assert callable(policy.CalcMrcaUncertaintyRelUpperBound)
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
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_eq(fixed_resolution):
    policy = fixed_resolution_algo.Policy(fixed_resolution)
    assert policy == policy
    assert policy == fixed_resolution_algo.Policy(fixed_resolution)
    assert not policy == policy.WithoutCalcRankAtColumnIndex()
    assert (
        policy.WithoutCalcRankAtColumnIndex()
        == policy.WithoutCalcRankAtColumnIndex()
    )
    assert not policy == fixed_resolution_algo.Policy(fixed_resolution + 1)


@pytest.mark.parametrize(
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_pickle(fixed_resolution):
    original = fixed_resolution_algo.Policy(fixed_resolution)
    with tempfile.TemporaryDirectory() as tmp_path:
        with open(f"{tmp_path}/data", "wb") as tmp_file:
            pickle.dump(original, tmp_file)

        with open(f"{tmp_path}/data", "rb") as tmp_file:
            reconstituted = pickle.load(tmp_file)
            assert reconstituted == original


@pytest.mark.parametrize(
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_GetSpec(fixed_resolution):
    assert fixed_resolution_algo.Policy(
        fixed_resolution
    ).GetSpec() == fixed_resolution_algo.PolicySpec(fixed_resolution)


@pytest.mark.parametrize(
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_WithoutCalcRankAtColumnIndex(fixed_resolution):

    original = fixed_resolution_algo.Policy(fixed_resolution)
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
        fixed_resolution_algo.Policy(
            fixed_resolution,
        ).WithoutCalcRankAtColumnIndex()
        == stripped
    )


def test_repr():
    fixed_resolution = 1
    policy = fixed_resolution_algo.Policy(fixed_resolution)
    assert str(fixed_resolution) in repr(policy)
    assert policy.GetSpec().GetAlgoIdentifier() in repr(policy)


def test_str():
    fixed_resolution = 1
    policy = fixed_resolution_algo.Policy(fixed_resolution)
    assert str(fixed_resolution) in str(policy)
    assert policy.GetSpec().GetAlgoTitle() in str(policy)
