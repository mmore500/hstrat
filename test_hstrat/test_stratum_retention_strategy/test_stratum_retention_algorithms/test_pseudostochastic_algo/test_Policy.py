import pickle
import tempfile

import pytest

from hstrat.hstrat import pseudostochastic_algo


@pytest.mark.parametrize(
    "hash_salt",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_init(hash_salt):
    assert (
        pseudostochastic_algo.Policy(hash_salt).GetSpec()
        == pseudostochastic_algo.Policy(
            policy_spec=pseudostochastic_algo.PolicySpec(hash_salt),
        ).GetSpec()
    )

    policy = pseudostochastic_algo.Policy(hash_salt)

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
    "hash_salt",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_eq(hash_salt):
    policy = pseudostochastic_algo.Policy(hash_salt)
    assert policy == policy
    assert policy == pseudostochastic_algo.Policy(hash_salt)
    assert policy == policy.WithoutCalcRankAtColumnIndex()
    assert (
        policy.WithoutCalcRankAtColumnIndex()
        == policy.WithoutCalcRankAtColumnIndex()
    )
    assert not policy == pseudostochastic_algo.Policy(hash_salt + 1)


@pytest.mark.parametrize(
    "hash_salt",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_pickle(hash_salt):
    original = pseudostochastic_algo.Policy(hash_salt)
    with tempfile.TemporaryDirectory() as tmp_path:
        with open(f"{tmp_path}/data", "wb") as tmp_file:
            pickle.dump(original, tmp_file)

        with open(f"{tmp_path}/data", "rb") as tmp_file:
            reconstituted = pickle.load(tmp_file)
            assert reconstituted == original


@pytest.mark.parametrize(
    "hash_salt",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_GetSpec(hash_salt):
    assert pseudostochastic_algo.Policy(
        hash_salt
    ).GetSpec() == pseudostochastic_algo.PolicySpec(hash_salt)


@pytest.mark.parametrize(
    "hash_salt",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_WithoutCalcRankAtColumnIndex(hash_salt):

    original = pseudostochastic_algo.Policy(hash_salt)
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
        pseudostochastic_algo.Policy(
            hash_salt,
        ).WithoutCalcRankAtColumnIndex()
        == stripped
    )


def test_repr():
    hash_salt = 1
    policy = pseudostochastic_algo.Policy(hash_salt)
    assert str(hash_salt) in repr(policy)
    assert policy.GetSpec().GetAlgoIdentifier() in repr(policy)


def test_str():
    hash_salt = 1
    policy = pseudostochastic_algo.Policy(hash_salt)
    assert str(hash_salt) in str(policy)
    assert policy.GetSpec().GetAlgoTitle() in str(policy)
