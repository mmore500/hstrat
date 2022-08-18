import itertools as it
import numbers
import random

from iterpop import iterpop as ip
import numpy as np
import pytest

from hstrat2.helpers import pairwise
from hstrat2.hstrat import stochastic_policy


@pytest.mark.parametrize(
    'replicate',
    range(5),
)
def test_policy_consistency(replicate):
    random.seed(replicate)
    policy = stochastic_policy.Policy()
    spec = policy.GetSpec()
    assert stochastic_policy.IterRetainedRanks is None
