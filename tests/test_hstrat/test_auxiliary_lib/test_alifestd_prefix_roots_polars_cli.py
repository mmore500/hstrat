import os
import subprocess

import pandas as pd

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_prefix_roots_polars_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_prefix_roots_polars",
            "--help",
        ],
        check=True,
    )


def test_alifestd_prefix_roots_polars_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_prefix_roots_polars",
            "--version",
        ],
        check=True,
    )
