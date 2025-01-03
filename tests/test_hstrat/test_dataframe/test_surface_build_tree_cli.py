import os
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


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
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_build_tree",
            "/tmp/hstrat_surface_build_tree.csv",
        ],
        check=True,
        input=f"{assets}/packed.csv".encode(),
    )


def test_surface_build_tree_cli_parquet():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_build_tree",
            "/tmp/hstrat_surface_build_tree.pqt",
            "--shrink-dtypes",
            "--exploded-slice-size",
            "50_000_000",
        ],
        check=True,
        input=f"{assets}/packed.csv".encode(),
    )
