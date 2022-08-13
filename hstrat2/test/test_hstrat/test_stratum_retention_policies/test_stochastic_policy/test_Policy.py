import pytest
import random

from hstrat2.hstrat import stochastic_policy


@pytest.mark.parametrize(
    'replicate',
    range(5),
)
def test_init(replicate):
    random.seed(replicate)
    assert (
        stochastic_policy.Policy().GetSpec()
        == stochastic_policy.Policy(
            policy_spec=stochastic_policy.PolicySpec(),
        ).GetSpec()
    )

    policy = stochastic_policy.Policy()

    # invariants
    assert callable(policy.CalcMrcaUncertaintyAbsUpperBound)
    assert callable(policy.CalcMrcaUncertaintyAbsUpperBoundPessimalRank)
    assert callable(policy.CalcMrcaUncertaintyRelUpperBound)
    assert callable(policy.CalcNumStrataRetainedUpperBound)
    # scrying
    assert policy.CalcMrcaUncertaintyAbsExact is None
    assert policy.CalcMrcaUncertaintyRelExact is None
    assert policy.CalcNumStrataRetainedExact is None
    assert policy.CalcRankAtColumnIndex is None
    assert policy.IterRetainedRanks is None
    # enactment
    assert callable(policy.GenDropRanks)


@pytest.mark.parametrize(
    'replicate',
    range(5),
)
def test_eq(replicate):
    random.seed(replicate)
    policy = stochastic_policy.Policy()
    assert policy == policy
    assert policy == stochastic_policy.Policy()
    assert policy == policy.WithoutCalcRankAtColumnIndex()
    assert policy.WithoutCalcRankAtColumnIndex() \
        == policy.WithoutCalcRankAtColumnIndex()

@pytest.mark.parametrize(
    'replicate',
    range(5),
)
def test_GetSpec(replicate):
    random.seed(replicate)
    assert stochastic_policy.Policy().GetSpec() \
        == stochastic_policy.PolicySpec()

@pytest.mark.parametrize(
    'replicate',
    range(5),
)
def test_WithoutCalcRankAtColumnIndex(replicate):
    random.seed(replicate)

    original = stochastic_policy.Policy()
    stripped = original.WithoutCalcRankAtColumnIndex()

    assert stripped.CalcRankAtColumnIndex is None

    assert original.CalcMrcaUncertaintyAbsUpperBound \
        == stripped.CalcMrcaUncertaintyAbsUpperBound
    assert original.CalcMrcaUncertaintyAbsUpperBoundPessimalRank \
        == stripped.CalcMrcaUncertaintyAbsUpperBoundPessimalRank
    assert original.CalcMrcaUncertaintyRelUpperBound \
        == stripped.CalcMrcaUncertaintyRelUpperBound
    assert original.CalcNumStrataRetainedUpperBound \
        == stripped.CalcNumStrataRetainedUpperBound
    # scrying
    assert original.CalcMrcaUncertaintyAbsExact \
        == stripped.CalcMrcaUncertaintyAbsExact
    assert original.CalcMrcaUncertaintyRelExact \
        == stripped.CalcMrcaUncertaintyRelExact
    assert original.CalcNumStrataRetainedExact \
        == stripped.CalcNumStrataRetainedExact
    assert original.IterRetainedRanks == stripped.IterRetainedRanks
    # enactment
    assert original.GenDropRanks == stripped.GenDropRanks

    # test chaining
    assert stochastic_policy.Policy().WithoutCalcRankAtColumnIndex() \
        == stripped

def test_repr():
    policy = stochastic_policy.Policy()
    assert policy.GetSpec().GetPolicyName() in repr(policy)

def test_str():
    policy = stochastic_policy.Policy()
    assert policy.GetSpec().GetPolicyTitle() in str(policy)
