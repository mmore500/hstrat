"""Configuration file for pytest."""

import random

import numpy as np
import pytest


@pytest.fixture(autouse=True)
def reseed_random(request: pytest.FixtureRequest) -> None:
    """Reseed random number generator to ensure determinstic test."""
    seed = hash(request.node.name) % 2**32
    random.seed(seed)
    np.random.seed(seed)
