from hstrat.hstrat import perfect_resolution_algo


def test_eq():
    spec = perfect_resolution_algo.PolicySpec()
    assert spec == spec
    assert spec == perfect_resolution_algo.PolicySpec()


def test_init():
    pass


def test_GetAlgoIdentifier():
    spec = perfect_resolution_algo.PolicySpec()
    assert spec.GetAlgoIdentifier()


def test_GetAlgoTitle():
    spec = perfect_resolution_algo.PolicySpec()
    assert spec.GetAlgoTitle()


def test_repr():
    spec = perfect_resolution_algo.PolicySpec()
    assert spec.GetAlgoIdentifier() in repr(spec)


def test_str():
    spec = perfect_resolution_algo.PolicySpec()
    assert spec.GetAlgoTitle() in str(spec)
