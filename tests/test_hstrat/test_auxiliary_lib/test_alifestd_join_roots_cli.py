import os
import pathlib
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_join_roots_cli_help():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_join_roots",
            "--help",
        ],
        check=True,
    )


def test_alifestd_join_roots_cli_version():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_join_roots",
            "--version",
        ],
        check=True,
    )


def test_alifestd_join_roots_cli_csv():
    output_file = "/tmp/hstrat_alifestd_join_roots.csv"
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_join_roots",
            output_file,
        ],
        check=True,
        input=f"{assets}/example-standard-toy-asexual-phylogeny.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_join_roots_cli_parquet():
    output_file = "/tmp/hstrat_alifestd_join_roots.pqt"
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_join_roots",
            output_file,
        ],
        check=True,
        input=f"{assets}/example-standard-toy-asexual-phylogeny.csv".encode(),
    )
    assert os.path.exists(output_file)
