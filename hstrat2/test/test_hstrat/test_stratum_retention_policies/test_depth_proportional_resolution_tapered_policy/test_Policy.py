import pytest

from hstrat2.hstrat import depth_proportional_resolution_tapered_policy


@pytest.mark.parametrize(
    'depth_proportional_resolution',
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
        depth_proportional_resolution_tapered_policy.Policy(depth_proportional_resolution).GetSpec()
        == depth_proportional_resolution_tapered_policy.Policy(
            policy_spec=depth_proportional_resolution_tapered_policy.PolicySpec(depth_proportional_resolution),
        ).GetSpec()
    )

    policy = depth_proportional_resolution_tapered_policy.Policy(depth_proportional_resolution)

    # invariants
    assert callable(policy.CalcMrcaUncertaintyUpperBound)
    assert callable(policy.CalcNumStrataRetainedUpperBound)
    # scrying
    assert callable(policy.CalcMrcaUncertaintyExact)
    assert callable(policy.CalcNumStrataRetainedExact)
    assert callable(policy.CalcRankAtColumnIndex)
    assert callable(policy.IterRetainedRanks)
    # enactment
    assert callable(policy.GenDropRanks)


@pytest.mark.parametrize(
    'depth_proportional_resolution',
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
    policy = depth_proportional_resolution_tapered_policy.Policy(depth_proportional_resolution)
    assert policy == policy
    assert policy == depth_proportional_resolution_tapered_policy.Policy(depth_proportional_resolution)
    assert not policy == policy.WithoutCalcRankAtColumnIndex()
    assert policy.WithoutCalcRankAtColumnIndex() \
        == policy.WithoutCalcRankAtColumnIndex()
    assert not policy == depth_proportional_resolution_tapered_policy.Policy(depth_proportional_resolution + 1)

@pytest.mark.parametrize(
    'depth_proportional_resolution',
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
    assert depth_proportional_resolution_tapered_policy.Policy(depth_proportional_resolution).GetSpec() \
        == depth_proportional_resolution_tapered_policy.PolicySpec(depth_proportional_resolution)

@pytest.mark.parametrize(
    'depth_proportional_resolution',
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

    original = depth_proportional_resolution_tapered_policy.Policy(depth_proportional_resolution)
    stripped = original.WithoutCalcRankAtColumnIndex()

    assert stripped.CalcRankAtColumnIndex is None

    assert original.CalcMrcaUncertaintyUpperBound \
        == stripped.CalcMrcaUncertaintyUpperBound
    assert original.CalcNumStrataRetainedUpperBound \
        == stripped.CalcNumStrataRetainedUpperBound
    # scrying
    assert original.CalcMrcaUncertaintyExact \
        == stripped.CalcMrcaUncertaintyExact
    assert original.CalcNumStrataRetainedExact \
        == stripped.CalcNumStrataRetainedExact
    assert original.IterRetainedRanks == stripped.IterRetainedRanks
    # enactment
    assert original.GenDropRanks == stripped.GenDropRanks

    # test chaining
    assert depth_proportional_resolution_tapered_policy.Policy(
        depth_proportional_resolution,
    ).WithoutCalcRankAtColumnIndex() == stripped
