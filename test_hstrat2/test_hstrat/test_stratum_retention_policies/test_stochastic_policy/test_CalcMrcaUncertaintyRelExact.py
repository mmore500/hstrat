import random

import pytest

from hstrat2.hstrat import stochastic_policy


@pytest.mark.parametrize(
    "replicate",
    range(5),
)
def test_policy_consistency(replicate):
    random.seed(replicate)
    assert stochastic_policy.CalcMrcaUncertaintyRelExact is None
