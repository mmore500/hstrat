import pickle
import tempfile

import pytest

from hstrat.hstrat import depth_proportional_resolution_algo


@pytest.mark.parametrize(
    "depth_proportional_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_init(depth_proportional_resolution):
    assert (
        depth_proportional_resolution_algo.Policy(
            depth_proportional_resolution
        ).GetSpec()
        == depth_proportional_resolution_algo.Policy(
            policy_spec=depth_proportional_resolution_algo.PolicySpec(
                depth_proportional_resolution
            ),
        ).GetSpec()
    )

    policy = depth_proportional_resolution_algo.Policy(
        depth_proportional_resolution
    )

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
    "depth_proportional_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_pickle(depth_proportional_resolution):
    original = depth_proportional_resolution_algo.Policy(
        depth_proportional_resolution
    )
    with tempfile.TemporaryDirectory() as tmp_path:
        with open(f"{tmp_path}/data", "wb") as tmp_file:
            pickle.dump(original, tmp_file)

        with open(f"{tmp_path}/data", "rb") as tmp_file:
            reconstituted = pickle.load(tmp_file)
            assert reconstituted == original


@pytest.mark.parametrize(
    "depth_proportional_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_eq(depth_proportional_resolution):
    policy = depth_proportional_resolution_algo.Policy(
        depth_proportional_resolution
    )
    assert policy == policy
    assert policy == depth_proportional_resolution_algo.Policy(
        depth_proportional_resolution
    )
    assert not policy == policy.WithoutCalcRankAtColumnIndex()
    assert (
        policy.WithoutCalcRankAtColumnIndex()
        == policy.WithoutCalcRankAtColumnIndex()
    )
    assert not policy == depth_proportional_resolution_algo.Policy(
        depth_proportional_resolution + 1
    )


@pytest.mark.parametrize(
    "depth_proportional_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_GetSpec(depth_proportional_resolution):
    assert depth_proportional_resolution_algo.Policy(
        depth_proportional_resolution
    ).GetSpec() == depth_proportional_resolution_algo.PolicySpec(
        depth_proportional_resolution
    )


@pytest.mark.parametrize(
    "depth_proportional_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_WithoutCalcRankAtColumnIndex(depth_proportional_resolution):

    original = depth_proportional_resolution_algo.Policy(
        depth_proportional_resolution
    )
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
        depth_proportional_resolution_algo.Policy(
            depth_proportional_resolution,
        ).WithoutCalcRankAtColumnIndex()
        == stripped
    )


def test_repr():
    depth_proportional_resolution = 1
    policy = depth_proportional_resolution_algo.Policy(
        depth_proportional_resolution,
    )
    assert str(depth_proportional_resolution) in repr(policy)
    assert policy.GetSpec().GetAlgoIdentifier() in repr(policy)


def test_str():
    depth_proportional_resolution = 1
    policy = depth_proportional_resolution_algo.Policy(
        depth_proportional_resolution,
    )
    assert str(depth_proportional_resolution) in str(policy)
    assert policy.GetSpec().GetAlgoTitle() in str(policy)
