import random

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
