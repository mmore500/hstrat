import pytest

from hstrat2.hstrat import pseudostochastic_policy


@pytest.mark.parametrize(
    'random_seed',
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_init(random_seed):
    assert (
        pseudostochastic_policy.Policy(random_seed).GetSpec()
        == pseudostochastic_policy.Policy(
            policy_spec=pseudostochastic_policy.PolicySpec(random_seed),
        ).GetSpec()
    )

    policy = pseudostochastic_policy.Policy(random_seed)

    # invariants
    assert callable(policy.CalcMrcaUncertaintyAbsUpperBound)
    assert callable(policy.CalcNumStrataRetainedUpperBound)
    # scrying
    assert policy.CalcMrcaUncertaintyAbsExact is None
    assert policy.CalcNumStrataRetainedExact is None
    assert policy.CalcRankAtColumnIndex is None
    assert policy.IterRetainedRanks is None
    # enactment
    assert callable(policy.GenDropRanks)


@pytest.mark.parametrize(
    'random_seed',
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_eq(random_seed):
    policy = pseudostochastic_policy.Policy(random_seed)
    assert policy == policy
    assert policy == pseudostochastic_policy.Policy(random_seed)
    assert policy == policy.WithoutCalcRankAtColumnIndex()
    assert policy.WithoutCalcRankAtColumnIndex() \
        == policy.WithoutCalcRankAtColumnIndex()
    assert not policy == pseudostochastic_policy.Policy(random_seed + 1)

@pytest.mark.parametrize(
    'random_seed',
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_GetSpec(random_seed):
    assert pseudostochastic_policy.Policy(random_seed).GetSpec() \
        == pseudostochastic_policy.PolicySpec(random_seed)

@pytest.mark.parametrize(
    'random_seed',
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_WithoutCalcRankAtColumnIndex(random_seed):

    original = pseudostochastic_policy.Policy(random_seed)
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
    assert pseudostochastic_policy.Policy(
        random_seed,
    ).WithoutCalcRankAtColumnIndex() == stripped

def test_repr():
    random_seed = 1
    policy = pseudostochastic_policy.Policy(random_seed)
    assert str(random_seed) in repr(policy)
    assert policy.GetSpec().GetPolicyName() in repr(policy)

def test_str():
    random_seed = 1
    policy = pseudostochastic_policy.Policy(random_seed)
    assert str(random_seed) in str(policy)
    assert policy.GetSpec().GetPolicyTitle() in str(policy)
