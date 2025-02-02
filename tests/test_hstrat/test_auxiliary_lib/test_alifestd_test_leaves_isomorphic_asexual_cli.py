import os
import subprocess

import pytest

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_test_leaves_isomorphic_asexual_cli_help():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_test_leaves_isomorphic_asexual",
            "--help",
        ],
        check=True,
    )


def test_alifestd_test_leaves_isomorphic_asexual_cli_version():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_test_leaves_isomorphic_asexual",
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
def test_alifestd_test_leaves_isomorphic_asexual_cli_csv1(input_file: str):
    cmd = [
        "python3",
        "-m",
        "hstrat._auxiliary_lib._alifestd_test_leaves_isomorphic_asexual",
        f"{assets}/{input_file}",
        f"{assets}/{input_file}",
        "--taxon-label",
        "id",
    ]
    result = subprocess.run(cmd)
    assert result.returncode == 0


def test_alifestd_test_leaves_isomorphic_asexual_cli_csv2():
    cmd = [
        "python3",
        "-m",
        "hstrat._auxiliary_lib._alifestd_test_leaves_isomorphic_asexual",
        f"{assets}/nk_ecoeaselection.csv",
        f"{assets}/nk_lexicaseselection.csv",
        "--taxon-label",
        "id",
    ]
    result = subprocess.run(cmd)
    assert result.returncode == 1
