import pytest

from hstrat.hstrat import recency_proportional_resolution_curbed_algo


@pytest.mark.parametrize(
    "size_curb",
    [
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_init(size_curb):
    assert (
        recency_proportional_resolution_curbed_algo.Policy(size_curb).GetSpec()
        == recency_proportional_resolution_curbed_algo.Policy(
            policy_spec=recency_proportional_resolution_curbed_algo.PolicySpec(
                size_curb
            ),
        ).GetSpec()
    )

    policy = recency_proportional_resolution_curbed_algo.Policy(size_curb)

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
    "size_curb",
    [
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_eq(size_curb):
    policy = recency_proportional_resolution_curbed_algo.Policy(size_curb)
    assert policy == policy
    assert policy == recency_proportional_resolution_curbed_algo.Policy(
        size_curb
    )
    assert not policy == policy.WithoutCalcRankAtColumnIndex()
    assert (
        policy.WithoutCalcRankAtColumnIndex()
        == policy.WithoutCalcRankAtColumnIndex()
    )
    assert not policy == recency_proportional_resolution_curbed_algo.Policy(
        size_curb + 1
    )


@pytest.mark.parametrize(
    "size_curb",
    [
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_GetSpec(size_curb):
    assert recency_proportional_resolution_curbed_algo.Policy(
        size_curb
    ).GetSpec() == recency_proportional_resolution_curbed_algo.PolicySpec(
        size_curb
    )


@pytest.mark.parametrize(
    "size_curb",
    [
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_WithoutCalcRankAtColumnIndex(size_curb):

    original = recency_proportional_resolution_curbed_algo.Policy(size_curb)
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
        recency_proportional_resolution_curbed_algo.Policy(
            size_curb,
        ).WithoutCalcRankAtColumnIndex()
        == stripped
    )


def test_repr():
    size_curb = 1
    policy = recency_proportional_resolution_curbed_algo.Policy(size_curb)
    assert str(size_curb) in repr(policy)
    assert policy.GetSpec().GetAlgoIdentifier() in repr(policy)


def test_str():
    size_curb = 1
    policy = recency_proportional_resolution_curbed_algo.Policy(size_curb)
    assert str(size_curb) in str(policy)
    assert policy.GetSpec().GetAlgoTitle() in str(policy)
