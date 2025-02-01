import os
import subprocess

import pytest

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_count_root_nodes_cli_help():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_count_root_nodes",
            "--help",
        ],
        check=True,
    )


def test_alifestd_count_root_nodes_cli_version():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_count_root_nodes",
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
def test_alifestd_count_root_nodes_cli_csv1(input_file: str):
    cmd = [
        "python3",
        "-m",
        "hstrat._auxiliary_lib._alifestd_count_root_nodes",
        f"{assets}/{input_file}",
    ]
    result = subprocess.run(cmd, capture_output=True, check=True, text=True)
    assert result.stdout.strip() == "1"


@pytest.mark.parametrize(
    "input_file",
    [
        "example-standard-toy-asexual-phylogeny-tworoots.csv",
    ],
)
def test_alifestd_count_root_nodes_cli_csv2(input_file: str):
    cmd = [
        "python3",
        "-m",
        "hstrat._auxiliary_lib._alifestd_count_root_nodes",
        f"{assets}/{input_file}",
    ]
    result = subprocess.run(cmd, capture_output=True, check=True, text=True)
    assert result.stdout.strip() == "2"
