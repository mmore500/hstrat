from hstrat.hstrat import nominal_resolution_algo


def test_eq():
    spec = nominal_resolution_algo.PolicySpec()
    assert spec == spec
    assert spec == nominal_resolution_algo.PolicySpec()


def test_init():
    pass


def test_GetAlgoName():
    spec = nominal_resolution_algo.PolicySpec()
    assert spec.GetAlgoName()


def test_GetAlgoTitle():
    spec = nominal_resolution_algo.PolicySpec()
    assert spec.GetAlgoTitle()


def test_repr():
    spec = nominal_resolution_algo.PolicySpec()
    assert spec.GetAlgoName() in repr(spec)


def test_str():
    spec = nominal_resolution_algo.PolicySpec()
    assert spec.GetAlgoTitle() in str(spec)
