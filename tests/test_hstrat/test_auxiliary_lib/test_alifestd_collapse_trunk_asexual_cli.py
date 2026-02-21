import os
import subprocess

import pandas as pd

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_collapse_trunk_asexual_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_collapse_trunk_asexual",
            "--help",
        ],
        check=True,
    )


def test_alifestd_collapse_trunk_asexual_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_collapse_trunk_asexual",
            "--version",
        ],
        check=True,
    )
