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
    output_file = "/tmp/hstrat_surface_test_drive.csv"  # nosec B108
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
    output_file = "/tmp/hstrat_surface_test_drive.pqt"  # nosec B108
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


def test_surface_test_drive_cli_flags():
    output_file = "/tmp/hstrat_surface_test_drive_flags.pqt"  # nosec B108
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_test_drive",
            output_file,
            "--shrink-dtypes",
            "--stratum-differentia-bit-width",
            "8",
            "--dstream-algo",
            "dstream.primed_4pad0_tiltedxtc_algo",
            "--dstream-S",
            "36",
            "--dstream-T-bitwidth",
            "64",
        ],
        check=True,
        input=f"{assets}/nk_ecoeaselection.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_surface_test_drive_cli_pipe_reconstruct():
    output_file = "/tmp/hstrat_surface_test_drive_reconstruct.pqt"  # nosec B108
    pathlib.Path(output_file).unlink(missing_ok=True)
    td = subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_test_drive",
            "/dev/stdout",
            "--shrink-dtypes",
            "--output-filetype",
            "parquet",
            "--write-kwarg",
            "compression='uncompressed'",
        ],
        capture_output=True,
        check=True,
        input=f"{assets}/nk_ecoeaselection.csv".encode(),
    )
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_build_tree",
            output_file,
            "--stdin",
            "--input-filetype",
            "parquet",
        ],
        check=True,
        input=td.stdout,
    )
    assert os.path.exists(output_file)
