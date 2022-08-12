from hstrat2.hstrat import perfect_resolution_policy


def test_eq():
    spec = perfect_resolution_policy.PolicySpec()
    assert spec == spec
    assert spec == perfect_resolution_policy.PolicySpec()

def test_init():
    pass

def test_GetPolicyName():
    spec = perfect_resolution_policy.PolicySpec()
    assert spec.GetPolicyName()

def test_GetPolicyTitle():
    spec = perfect_resolution_policy.PolicySpec()
    assert spec.GetPolicyTitle()
