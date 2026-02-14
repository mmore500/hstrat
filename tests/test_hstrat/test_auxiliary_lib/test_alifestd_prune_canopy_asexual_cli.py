import os
import pathlib
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_prune_canopy_asexual_cli_help():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_prune_canopy_asexual",
            "--help",
        ],
        check=True,
    )


def test_alifestd_prune_canopy_asexual_cli_version():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_prune_canopy_asexual",
            "--version",
        ],
        check=True,
    )


def test_alifestd_prune_canopy_asexual_cli_csv():
    output_file = "/tmp/hstrat_alifestd_prune_canopy_asexual.csv"
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_prune_canopy_asexual",
            "-n",
            "1",
            output_file,
        ],
        check=True,
        input=f"{assets}/example-standard-toy-asexual-phylogeny.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_prune_canopy_asexual_cli_parquet():
    output_file = "/tmp/hstrat_alifestd_prune_canopy_asexual.pqt"
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_prune_canopy_asexual",
            "-n",
            "1",
            output_file,
        ],
        check=True,
        input=f"{assets}/example-standard-toy-asexual-phylogeny.csv".encode(),
    )
    assert os.path.exists(output_file)
