import os
import pathlib
import subprocess

import polars as pl

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
    output_file = "/tmp/hstrat_surface_build_tree.csv"  # nosec B108
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
    output_file = "/tmp/hstrat_surface_build_tree.pqt"  # nosec B108
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


def test_surface_build_tree_cli_no_drop_dstream_metadata():
    output_file = "/tmp/hstrat_surface_build_tree_no_drop.pqt"  # nosec B108
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_build_tree",
            output_file,
            "--no-drop-dstream-metadata",
        ],
        check=True,
        input=f"{assets}/packed.csv".encode(),
    )
    assert os.path.exists(output_file)
    res = pl.read_parquet(output_file)
    dstream_cols = [c for c in res.columns if c.startswith("dstream_")]
    # should have more than just dstream_data_id
    assert len(dstream_cols) > 1


def test_surface_build_tree_cli_drop_dstream_metadata_fails():
    output_file = "/tmp/hstrat_surface_build_tree_drop.pqt"  # nosec B108
    pathlib.Path(output_file).unlink(missing_ok=True)
    result = subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_build_tree",
            output_file,
            "--drop-dstream-metadata",
        ],
        input=f"{assets}/packed.csv".encode(),
    )
    assert result.returncode != 0
