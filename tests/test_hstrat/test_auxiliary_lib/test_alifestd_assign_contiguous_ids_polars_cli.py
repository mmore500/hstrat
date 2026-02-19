import os
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_assign_contiguous_ids_polars_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_assign_contiguous_ids_polars",
            "--help",
        ],
        check=True,
    )


def test_alifestd_assign_contiguous_ids_polars_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_assign_contiguous_ids_polars",
            "--version",
        ],
        check=True,
    )
