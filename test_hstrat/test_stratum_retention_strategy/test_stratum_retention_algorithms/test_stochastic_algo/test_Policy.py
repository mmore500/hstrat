import pickle
import random
import tempfile

import pytest

from hstrat.hstrat import stochastic_algo


@pytest.mark.parametrize(
    "replicate",
    range(5),
)
def test_init(replicate):
    random.seed(replicate)
    assert (
        stochastic_algo.Policy().GetSpec()
        == stochastic_algo.Policy(
            policy_spec=stochastic_algo.PolicySpec(),
        ).GetSpec()
    )

    policy = stochastic_algo.Policy()

    # invariants
    assert callable(policy.CalcMrcaUncertaintyAbsUpperBound)
    assert callable(policy.CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank)
    assert callable(policy.CalcMrcaUncertaintyAbsUpperBoundPessimalRank)
    assert callable(policy.CalcMrcaUncertaintyRelUpperBound)
    assert callable(policy.CalcMrcaUncertaintyRelUpperBoundAtPessimalRank)
    assert callable(policy.CalcMrcaUncertaintyRelUpperBoundPessimalRank)
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
    "replicate",
    range(5),
)
def test_eq(replicate):
    random.seed(replicate)
    policy = stochastic_algo.Policy()
    assert policy == policy
    assert policy == stochastic_algo.Policy()
    assert policy == policy.WithoutCalcRankAtColumnIndex()
    assert (
        policy.WithoutCalcRankAtColumnIndex()
        == policy.WithoutCalcRankAtColumnIndex()
    )


def test_pickle():
    original = stochastic_algo.Policy()
    with tempfile.TemporaryDirectory() as tmp_path:
        with open(f"{tmp_path}/data", "wb") as tmp_file:
            pickle.dump(original, tmp_file)

        with open(f"{tmp_path}/data", "rb") as tmp_file:
            reconstituted = pickle.load(tmp_file)
            assert reconstituted == original


@pytest.mark.parametrize(
    "replicate",
    range(5),
)
def test_GetSpec(replicate):
    random.seed(replicate)
    assert stochastic_algo.Policy().GetSpec() == stochastic_algo.PolicySpec()


@pytest.mark.parametrize(
    "replicate",
    range(5),
)
def test_WithoutCalcRankAtColumnIndex(replicate):
    random.seed(replicate)

    original = stochastic_algo.Policy()
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
    assert stochastic_algo.Policy().WithoutCalcRankAtColumnIndex() == stripped


def test_repr():
    policy = stochastic_algo.Policy()
    assert policy.GetSpec().GetAlgoIdentifier() in repr(policy)


def test_str():
    policy = stochastic_algo.Policy()
    assert policy.GetSpec().GetAlgoTitle() in str(policy)
