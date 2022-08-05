import pytest

from hstrat2.hstrat import fixed_resolution_policy


@pytest.mark.parametrize(
    'fixed_resolution',
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
        fixed_resolution_policy.Policy(fixed_resolution).GetSpec()
        == fixed_resolution_policy.Policy(
            policy_spec=fixed_resolution_policy.PolicySpec(fixed_resolution),
        ).GetSpec()
    )

    policy = fixed_resolution_policy.Policy(fixed_resolution)

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
    'fixed_resolution',
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
    policy = fixed_resolution_policy.Policy(fixed_resolution)
    assert policy == policy
    assert policy == fixed_resolution_policy.Policy(fixed_resolution)
    assert not policy == policy.WithoutCalcRankAtColumnIndex()
    assert policy.WithoutCalcRankAtColumnIndex() \
        == policy.WithoutCalcRankAtColumnIndex()
    assert not policy == fixed_resolution_policy.Policy(fixed_resolution + 1)

@pytest.mark.parametrize(
    'fixed_resolution',
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
    assert fixed_resolution_policy.Policy(fixed_resolution).GetSpec() \
        == fixed_resolution_policy.PolicySpec(fixed_resolution)

@pytest.mark.parametrize(
    'fixed_resolution',
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

    original = fixed_resolution_policy.Policy(fixed_resolution)
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
    assert fixed_resolution_policy.Policy(
        fixed_resolution,
    ).WithoutCalcRankAtColumnIndex() == stripped
