"""Configuration file for pytest."""

import os
import random

import numpy as np
import pytest


@pytest.fixture(autouse=True)
def reseed_random(request: pytest.FixtureRequest) -> None:
    """Reseed random number generator to ensure determinstic test."""
    seed = hash(request.node.name) % 2**32
    random.seed(seed)
    np.random.seed(seed)


def pytest_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """

    print("env CXX:", os.environ.get("CXX", None))
    print(
        "env HSTRAT_CPPIMPORT_OPT_IN:",
        os.environ.get("HSTRAT_CPPIMPORT_OPT_IN", None),
    )
    print(
        "env HSTRAT_RERAISE_IMPORT_NATIVE_EXCEPTION:",
        os.environ.get("HSTRAT_RERAISE_IMPORT_NATIVE_EXCEPTION", None),
    )
