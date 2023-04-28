"""Configuration file for pytest."""

import os
import random
import warnings

import numpy as np
import pkg_resources
import pytest


def pytest_configure(config):
    print("env CXX:", os.environ.get("CXX", None))
    print(
        "env HSTRAT_CPPIMPORT_OPT_IN:",
        os.environ.get("HSTRAT_CPPIMPORT_OPT_IN", None),
    )
    print(
        "env HSTRAT_RERAISE_IMPORT_NATIVE_EXCEPTION:",
        os.environ.get("HSTRAT_RERAISE_IMPORT_NATIVE_EXCEPTION", None),
    )  # check for testing requirements
    # provide install instructions if they're missing
    try:
        from hstrat._auxiliary_lib._check_testing_requirements import (
            check_testing_requirements,
        )

        check_testing_requirements()
    except (
        ModuleNotFoundError,
        pkg_resources.DistributionNotFound,
        pkg_resources.VersionConflict,
    ) as exception:
        warnings.warn(
            "Missing some testing requirements. "
            "For instructions on installing dev dependencies, see "
            "https://hstrat.readthedocs.io/en/latest/contributing.html "
            "or CONTRIBUTING.rst"
            "\n"
            '  (Warning caused by exception "' + str(exception) + '".)'
        )


@pytest.fixture(autouse=True)
def reseed_random(request: pytest.FixtureRequest) -> None:
    """Reseed random number generator to ensure determinstic test."""
    random.seed(request.node.name)
    np.random.seed(random.randint(1, 2**32))
