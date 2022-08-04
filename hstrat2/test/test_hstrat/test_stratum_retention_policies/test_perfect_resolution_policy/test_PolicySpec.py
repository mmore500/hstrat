from hstrat2.hstrat import perfect_resolution_policy


def test_eq():
    spec = perfect_resolution_policy.PolicySpec()
    assert spec == spec
    assert spec == perfect_resolution_policy.PolicySpec()

def test_init():
    pass
