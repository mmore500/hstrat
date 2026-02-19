import os
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_delete_trunk_asexual_polars_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_delete_trunk_asexual_polars",
            "--help",
        ],
        check=True,
    )


def test_alifestd_delete_trunk_asexual_polars_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_delete_trunk_asexual_polars",
            "--version",
        ],
        check=True,
    )
