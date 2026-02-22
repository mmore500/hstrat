import os
import subprocess

import pytest

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_count_leaf_nodes_cli_help():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_count_leaf_nodes",
            "--help",
        ],
        check=True,
    )


def test_alifestd_count_leaf_nodes_cli_version():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_count_leaf_nodes",
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
def test_alifestd_count_leaf_nodes_cli_csv(input_file: str):
    cmd = [
        "python3",
        "-m",
        "hstrat._auxiliary_lib._alifestd_count_leaf_nodes",
        f"{assets}/{input_file}",
    ]
    result = subprocess.run(cmd, capture_output=True, check=True, text=True)
    count = int(result.stdout.strip())
    assert count >= 0
