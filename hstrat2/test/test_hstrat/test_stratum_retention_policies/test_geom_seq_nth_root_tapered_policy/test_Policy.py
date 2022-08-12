import pytest

from hstrat2.hstrat import geom_seq_nth_root_tapered_policy


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
def test_init(degree, interspersal):
    assert (
        geom_seq_nth_root_tapered_policy.Policy(degree, interspersal).GetSpec()
        == geom_seq_nth_root_tapered_policy.Policy(
            policy_spec=geom_seq_nth_root_tapered_policy.PolicySpec(degree, interspersal),
        ).GetSpec()
    )

    policy = geom_seq_nth_root_tapered_policy.Policy(degree, interspersal)

    # invariants
    assert callable(policy.CalcMrcaUncertaintyAbsUpperBound)
    assert callable(policy.CalcNumStrataRetainedUpperBound)
    # scrying
    assert callable(policy.CalcMrcaUncertaintyAbsExact)
    assert callable(policy.CalcNumStrataRetainedExact)
    assert callable(policy.CalcRankAtColumnIndex)
    assert callable(policy.IterRetainedRanks)
    # enactment
    assert callable(policy.GenDropRanks)


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
    policy = geom_seq_nth_root_tapered_policy.Policy(degree, interspersal)
    assert policy == policy
    assert policy == geom_seq_nth_root_tapered_policy.Policy(degree, interspersal)
    assert not policy == policy.WithoutCalcRankAtColumnIndex()
    assert policy.WithoutCalcRankAtColumnIndex() \
        == policy.WithoutCalcRankAtColumnIndex()
    assert not policy == geom_seq_nth_root_tapered_policy.Policy(degree, interspersal + 1)
    assert not policy == geom_seq_nth_root_tapered_policy.Policy(degree + 1, interspersal)
    assert not policy == geom_seq_nth_root_tapered_policy.Policy(degree + 1, interspersal + 1)

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
def test_GetSpec(degree, interspersal):
    assert geom_seq_nth_root_tapered_policy.Policy(degree, interspersal).GetSpec() \
        == geom_seq_nth_root_tapered_policy.PolicySpec(degree, interspersal)

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
def test_WithoutCalcRankAtColumnIndex(degree, interspersal):

    original = geom_seq_nth_root_tapered_policy.Policy(degree, interspersal)
    stripped = original.WithoutCalcRankAtColumnIndex()

    assert stripped.CalcRankAtColumnIndex is None

    assert original.CalcMrcaUncertaintyAbsUpperBound \
        == stripped.CalcMrcaUncertaintyAbsUpperBound
    assert original.CalcNumStrataRetainedUpperBound \
        == stripped.CalcNumStrataRetainedUpperBound
    # scrying
    assert original.CalcMrcaUncertaintyAbsExact \
        == stripped.CalcMrcaUncertaintyAbsExact
    assert original.CalcNumStrataRetainedExact \
        == stripped.CalcNumStrataRetainedExact
    assert original.IterRetainedRanks == stripped.IterRetainedRanks
    # enactment
    assert original.GenDropRanks == stripped.GenDropRanks

    # test chaining
    assert geom_seq_nth_root_tapered_policy.Policy(
        degree,
        interspersal,
    ).WithoutCalcRankAtColumnIndex() == stripped

def test_repr():
    degree = 1
    interspersal = 2
    policy = geom_seq_nth_root_tapered_policy.Policy(degree, interspersal)
    assert str(degree) in repr(policy)
    assert str(interspersal) in repr(policy)
    assert policy.GetSpec().GetPolicyName() in repr(policy)

def test_str():
    degree = 1
    interspersal = 2
    policy = geom_seq_nth_root_tapered_policy.Policy(degree, interspersal)
    assert str(degree) in str(policy)
    assert str(interspersal) in str(policy)
    assert policy.GetSpec().GetPolicyTitle() in str(policy)
