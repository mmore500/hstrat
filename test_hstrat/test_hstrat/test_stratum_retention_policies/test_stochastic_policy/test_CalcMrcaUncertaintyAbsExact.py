import random

import pytest

from hstrat.hstrat import stochastic_policy


@pytest.mark.parametrize(
    "replicate",
    range(5),
)
def test_policy_consistency(replicate):
    random.seed(replicate)
    assert stochastic_policy.CalcMrcaUncertaintyAbsExact is None
