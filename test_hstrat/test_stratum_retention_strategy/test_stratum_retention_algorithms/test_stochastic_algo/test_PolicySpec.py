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


def test_GetPolicyName():
    spec = stochastic_algo.PolicySpec()
    assert spec.GetPolicyName()


def test_GetPolicyTitle():
    spec = stochastic_algo.PolicySpec()
    assert spec.GetPolicyTitle()


def test_repr():
    spec = stochastic_algo.PolicySpec()
    assert spec.GetPolicyName() in repr(spec)


def test_str():
    spec = stochastic_algo.PolicySpec()
    assert spec.GetPolicyTitle() in str(spec)
