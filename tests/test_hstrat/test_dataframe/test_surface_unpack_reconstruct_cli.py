import os
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


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
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_unpack_reconstruct",
            "/tmp/hstrat_unpack_surface_reconstruct.csv",
        ],
        check=True,
        input=f"{assets}/packed.csv".encode(),
    )


def test_surface_unpack_reconstruct_cli_parquet():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_unpack_reconstruct",
            "/tmp/hstrat_unpack_surface_reconstruct.pqt",
            "--shrink-dtypes",
            "--exploded-slice-size",
            "50_000_000",
        ],
        check=True,
        input=f"{assets}/packed.csv".encode(),
    )
