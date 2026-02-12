import os
import pathlib
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_prune_extinct_lineages_asexual_polars_cli_help():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_prune_extinct_lineages_asexual_polars",
            "--help",
        ],
        check=True,
    )


def test_alifestd_prune_extinct_lineages_asexual_polars_cli_version():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_prune_extinct_lineages_asexual_polars",
            "--version",
        ],
        check=True,
    )


def test_alifestd_prune_extinct_lineages_asexual_polars_cli_csv():
    output_file = (
        "/tmp/hstrat_alifestd_prune_extinct_lineages_asexual_polars.csv"
    )
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_prune_extinct_lineages_asexual_polars",
            output_file,
        ],
        check=True,
        input=f"{assets}/prunetestphylo.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_prune_extinct_lineages_asexual_polars_cli_empty():
    output_file = (
        "/tmp/hstrat_alifestd_prune_extinct_lineages_asexual_polars.csv"
    )
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_prune_extinct_lineages_asexual_polars",
            output_file,
        ],
        check=True,
        input=f"{assets}/empty.csv".encode(),
    )
    assert os.path.exists(output_file)
