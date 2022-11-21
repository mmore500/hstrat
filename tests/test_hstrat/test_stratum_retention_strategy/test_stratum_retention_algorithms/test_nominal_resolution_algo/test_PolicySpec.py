import pickle
import tempfile

from hstrat.hstrat import nominal_resolution_algo


def test_eq():
    spec = nominal_resolution_algo.PolicySpec()
    assert spec == spec
    assert spec == nominal_resolution_algo.PolicySpec()


def test_pickle():
    original = nominal_resolution_algo.PolicySpec()
    with tempfile.TemporaryDirectory() as tmp_path:
        with open(f"{tmp_path}/data", "wb") as tmp_file:
            pickle.dump(original, tmp_file)

        with open(f"{tmp_path}/data", "rb") as tmp_file:
            reconstituted = pickle.load(tmp_file)
            assert reconstituted == original


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
