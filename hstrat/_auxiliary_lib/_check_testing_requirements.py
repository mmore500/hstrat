import importlib.metadata
import os

from packaging.requirements import InvalidRequirement
from packaging.requirements import Requirement


def check_testing_requirements() -> None:
    """Are all testing requirements available?

    If dependencies are missing, will raise
    importlib.metadata.PackageNotFoundError or ValueError.
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
    with open(testing_requirements_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                req = Requirement(line)
            except InvalidRequirement:
                continue
            version = importlib.metadata.version(req.name)
            if req.specifier and not req.specifier.contains(version):
                raise ValueError(
                    f"{req.name} {version} does not satisfy {req}"
                )
