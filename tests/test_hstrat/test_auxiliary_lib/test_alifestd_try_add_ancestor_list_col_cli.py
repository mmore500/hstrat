import os
import pathlib
import subprocess

import pytest

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_try_add_ancestor_list_col_cli_version():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_try_add_ancestor_list_col",
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
def test_alifestd_try_add_ancestor_list_col_cli_csv(input_file: str):
    output_file = f"/tmp/hstrat-{input_file}.pqt"
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_try_add_ancestor_list_col",
            output_file,
        ],
        check=True,
        input=f"{assets}/{input_file}".encode(),
    )
    assert os.path.exists(output_file)
