from hstrat.hstrat import nominal_resolution_algo


def test_eq():
    spec = nominal_resolution_algo.PolicySpec()
    assert spec == spec
    assert spec == nominal_resolution_algo.PolicySpec()


def test_init():
    pass


def test_GetAlgoIdentifier():
    spec = nominal_resolution_algo.PolicySpec()
    assert spec.GetAlgoIdentifier()


def test_GetAlgoTitle():
    spec = nominal_resolution_algo.PolicySpec()
    assert spec.GetAlgoTitle()


def test_repr():
    spec = nominal_resolution_algo.PolicySpec()
    assert spec.GetAlgoIdentifier() in repr(spec)


def test_str():
    spec = nominal_resolution_algo.PolicySpec()
    assert spec.GetAlgoTitle() in str(spec)
