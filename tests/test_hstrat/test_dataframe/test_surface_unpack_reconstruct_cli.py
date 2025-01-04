import os
import pathlib
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_surface_unpack_reconstruct_cli_help():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_unpack_reconstruct",
            "--help",
        ],
        check=True,
    )


def test_surface_unpack_reconstruct_cli_version():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_unpack_reconstruct",
            "--version",
        ],
        check=True,
    )


def test_surface_unpack_reconstruct_cli_csv():
    output_file = "/tmp/hstrat_unpack_surface_reconstruct.csv"
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_unpack_reconstruct",
            output_file,
        ],
        check=True,
        input=f"{assets}/packed.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_surface_unpack_reconstruct_cli_parquet():
    output_file = "/tmp/hstrat_unpack_surface_reconstruct.pqt"
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_unpack_reconstruct",
            output_file,
            "--shrink-dtypes",
            "--exploded-slice-size",
            "50_000_000",
        ],
        check=True,
        input=f"{assets}/packed.csv".encode(),
    )
    assert os.path.exists(output_file)
