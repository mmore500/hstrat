import os
import pathlib
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_surface_build_tree_cli_help():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_build_tree",
            "--help",
        ],
        check=True,
    )


def test_surface_build_tree_cli_version():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_build_tree",
            "--version",
        ],
        check=True,
    )


def test_surface_build_tree_cli_csv():
    output_file = "/tmp/hstrat_surface_build_tree.csv"
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_build_tree",
            output_file,
        ],
        check=True,
        input=f"{assets}/packed.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_surface_build_tree_cli_parquet():
    output_file = "/tmp/hstrat_surface_build_tree.pqt"
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_build_tree",
            output_file,
            "--shrink-dtypes",
            "--collapse-unif-freq",
            "0",
            "--exploded-slice-size",
            "50_000_000",
        ],
        check=True,
        input=f"{assets}/packed.csv".encode(),
    )
    assert os.path.exists(output_file)
