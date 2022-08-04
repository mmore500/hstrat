from hstrat2.hstrat import perfect_resolution_policy


def test_init():
    assert (
        perfect_resolution_policy.Policy().GetSpec()
        == perfect_resolution_policy.Policy(
            policy_spec=perfect_resolution_policy.PolicySpec(),
        ).GetSpec()
    )

    policy = perfect_resolution_policy.Policy()

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


def test_eq():
    policy = perfect_resolution_policy.Policy()
    assert policy == policy
    assert policy == perfect_resolution_policy.Policy()
    assert policy != policy.WithoutCalcRankAtColumnIndex()
    assert policy.WithoutCalcRankAtColumnIndex() \
        == policy.WithoutCalcRankAtColumnIndex()

def test_GetSpec():
    assert perfect_resolution_policy.Policy().GetSpec()

def test_WithoutCalcRankAtColumnIndex():

    original = perfect_resolution_policy.Policy()
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
    assert perfect_resolution_policy.Policy().WithoutCalcRankAtColumnIndex() \
        == stripped
