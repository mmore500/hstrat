import pickle
import random
import tempfile

import pytest

from hstrat.hstrat import stochastic_algo


@pytest.mark.parametrize(
    "replicate",
    range(5),
)
def test_eq(replicate):
    random.seed(replicate)
    spec = stochastic_algo.PolicySpec()
    assert spec == spec
    assert spec == stochastic_algo.PolicySpec()


def test_GetEvalCtor():
    # hstrat. is needed for eval()
    from hstrat import hstrat  # noqa

    spec = stochastic_algo.PolicySpec()
    reconstituted = eval(spec.GetEvalCtor())  # noqa
    eval_ctor = spec.GetEvalCtor()
    assert eval_ctor.startswith("hstrat.stochastic_algo.PolicySpec(")
    assert eval_ctor.endswith(")")
    reconstituted = eval(eval_ctor)  # noqa
    assert spec == reconstituted


def test_pickle():
    original = stochastic_algo.PolicySpec()
    with tempfile.TemporaryDirectory() as tmp_path:
        with open(f"{tmp_path}/data", "wb") as tmp_file:
            pickle.dump(original, tmp_file)

        with open(f"{tmp_path}/data", "rb") as tmp_file:
            reconstituted = pickle.load(tmp_file)
            assert reconstituted == original


@pytest.mark.parametrize(
    "replicate",
    range(5),
)
def test_init(replicate):
    random.seed(replicate)
    stochastic_algo.PolicySpec()


def test_GetAlgoIdentifier():
    spec = stochastic_algo.PolicySpec()
    assert spec.GetAlgoIdentifier()


def test_GetAlgoTitle():
    spec = stochastic_algo.PolicySpec()
    assert spec.GetAlgoTitle()


def test_repr():
    spec = stochastic_algo.PolicySpec()
    assert spec.GetAlgoIdentifier() in repr(spec)


def test_str():
    spec = stochastic_algo.PolicySpec()
    assert spec.GetAlgoTitle() in str(spec)
