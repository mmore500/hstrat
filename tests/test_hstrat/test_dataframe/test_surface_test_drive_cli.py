import os
import pathlib
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_surface_test_drive_cli_help():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_test_drive",
            "--help",
        ],
        check=True,
    )


def test_surface_test_drive_cli_version():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_test_drive",
            "--version",
        ],
        check=True,
    )


def test_surface_test_drive_cli_csv():
    output_file = "/tmp/hstrat_surface_test_drive.csv"
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_test_drive",
            output_file,
        ],
        check=True,
        input=f"{assets}/nk_ecoeaselection.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_surface_test_drive_cli_parquet():
    output_file = "/tmp/hstrat_surface_test_drive.pqt"
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_test_drive",
            output_file,
            "--shrink-dtypes",
        ],
        check=True,
        input=f"{assets}/nk_ecoeaselection.csv".encode(),
    )
    assert os.path.exists(output_file)
