import os
import subprocess

import pytest

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_count_unifurcations_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_count_unifurcations",
            "--help",
        ],
        check=True,
    )


def test_alifestd_count_unifurcations_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_count_unifurcations",
            "--version",
        ],
        check=True,
    )


@pytest.mark.parametrize(
    "input_file",
    [
        "nk_ecoeaselection.csv",
        "nk_lexicaseselection.csv",
        "nk_tournamentselection.csv",
    ],
)
def test_alifestd_count_unifurcations_cli_csv(input_file: str):
    cmd = [
        "python3",
        "-m",
        "hstrat._auxiliary_lib._alifestd_count_unifurcations",
        f"{assets}/{input_file}",
    ]
    result = subprocess.run(
        cmd, capture_output=True, check=True, text=True
    )  # nosec B603
    count = int(result.stdout.strip())
    assert count >= 0
