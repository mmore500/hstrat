from hstrat2.hstrat import pseudostochastic_policy


def test_policy_consistency():
    assert pseudostochastic_policy.CalcMrcaUncertaintyRelExact is None
