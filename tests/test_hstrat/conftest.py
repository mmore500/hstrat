"""Configuration file for pytest."""

import random
import warnings

import numpy as np
import pytest


def _warn_missing_requirements(exception):
    warnings.warn(
        "Missing some testing requirements. "
        "For instructions on installing dev dependencies, see "
        "https://hstrat.readthedocs.io/en/latest/contributing.html "
        "or CONTRIBUTING.rst"
        "\n"
        '  (Warning caused by exception "' + str(exception) + '".)'
    )


def pytest_configure(config):
    # check for testing requirements
    # provide install instructions if they're missing
    try:
        import pkg_resources
    except ModuleNotFoundError as exception:
        _warn_missing_requirements(exception)
        return

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
        _warn_missing_requirements(exception)


@pytest.fixture(autouse=True)
def reseed_random(request: pytest.FixtureRequest) -> None:
    """Reseed random number generator to ensure determinstic test."""
    random.seed(request.node.name)
    np.random.seed(random.randint(1, 2**32))
