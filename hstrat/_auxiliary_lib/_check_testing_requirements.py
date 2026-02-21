import os

import pkg_resources


# Adapted from https://stackoverflow.com/a/3787989
def check_testing_requirements() -> None:
    """Are all testing requirements available?

    If dependencies are missing, will raise pkg_resources.DistributionNotFound
    or pkg_resources.VersionConflict warning.
    """

    testing_requirements_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "requirements-dev",
            "requirements-testing.txt",
        )
    )
    with open(testing_requirements_path, "r") as testing_requirements:
        # adapted from https://stackoverflow.com/a/16298328
        pkg_resources.require(testing_requirements)
