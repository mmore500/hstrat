from hstrat.hstrat import pseudostochastic_algo


def test_policy_consistency():
    assert pseudostochastic_algo.CalcNumStrataRetainedExact is None
