import pytest
import random

from hstrat2.hstrat import stochastic_policy


@pytest.mark.parametrize(
    'replicate',
    range(5),
)
def test_eq(replicate):
    random.seed(replicate)
    spec = stochastic_policy.PolicySpec()
    assert spec == spec
    assert spec == stochastic_policy.PolicySpec()

@pytest.mark.parametrize(
    'replicate',
    range(5),
)
def test_init(replicate):
    random.seed(replicate)
    spec = stochastic_policy.PolicySpec()
