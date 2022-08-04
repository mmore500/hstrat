from hstrat2.hstrat import nominal_resolution_policy


def test_eq():
    spec = nominal_resolution_policy.PolicySpec()
    assert spec == spec
    assert spec == nominal_resolution_policy.PolicySpec()

def test_init():
    pass
