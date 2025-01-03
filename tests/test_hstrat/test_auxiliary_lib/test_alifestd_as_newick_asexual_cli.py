import os
import pathlib
import subprocess

import pytest

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_as_newick_asexual_cli_version():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_as_newick_asexual",
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
def test_alifestd_as_newick_asexual_cli_csv(input_file: str):
    output_file = f"/tmp/hstrat-{input_file}.newick"
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_as_newick_asexual",
            "--input-file",
            f"{assets}/{input_file}",
            "-o",
            output_file,
        ],
        check=True,
    )
    assert os.path.exists(output_file)
