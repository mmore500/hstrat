from hstrat.hstrat import nominal_resolution_algo


def test_eq():
    spec = nominal_resolution_algo.PolicySpec()
    assert spec == spec
    assert spec == nominal_resolution_algo.PolicySpec()


def test_init():
    pass


def test_GetPolicyName():
    spec = nominal_resolution_algo.PolicySpec()
    assert spec.GetPolicyName()


def test_GetPolicyTitle():
    spec = nominal_resolution_algo.PolicySpec()
    assert spec.GetPolicyTitle()


def test_repr():
    spec = nominal_resolution_algo.PolicySpec()
    assert spec.GetPolicyName() in repr(spec)


def test_str():
    spec = nominal_resolution_algo.PolicySpec()
    assert spec.GetPolicyTitle() in str(spec)
