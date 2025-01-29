import os
import pathlib
import subprocess
import typing

import pytest

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_as_newick_asexual_cli_help():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_as_newick_asexual",
            "--help",
        ],
        check=True,
    )


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
@pytest.mark.parametrize(
    "taxon_label",
    [
        None,
        "id",
    ],
)
def test_alifestd_as_newick_asexual_cli_csv(
    input_file: str, taxon_label: typing.Optional[str]
):
    output_file = f"/tmp/hstrat-{input_file}.newick"
    pathlib.Path(output_file).unlink(missing_ok=True)
    cmd = [
        "python3",
        "-m",
        "hstrat._auxiliary_lib._alifestd_as_newick_asexual",
        "--input-file",
        f"{assets}/{input_file}",
        "-o",
        output_file,
    ]
    if taxon_label is not None:
        cmd.extend(["--taxon-label", taxon_label])
    subprocess.run(cmd, check=True)
    assert os.path.exists(output_file)
