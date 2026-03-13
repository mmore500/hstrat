import os
import pathlib
import subprocess

import pandas as pd

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_collapse_unifurcations_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_collapse_unifurcations",
            "--help",
        ],
        check=True,
    )


def test_alifestd_collapse_unifurcations_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_collapse_unifurcations",
            "--version",
        ],
        check=True,
    )


def test_alifestd_collapse_unifurcations_cli_csv():
    output_file = (
        "/tmp/hstrat_alifestd_collapse_unifurcations.csv"  # nosec B108
    )
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_collapse_unifurcations",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=f"{assets}/collapse_unifurcations_testphylo.csv".encode(),
    )
    assert os.path.exists(output_file)
    result_df = pd.read_csv(output_file)
    assert len(result_df) > 0
    assert "id" in result_df.columns


def test_alifestd_collapse_unifurcations_cli_parquet():
    output_file = (
        "/tmp/hstrat_alifestd_collapse_unifurcations.pqt"  # nosec B108
    )
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_collapse_unifurcations",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=f"{assets}/collapse_unifurcations_testphylo.csv".encode(),
    )
    assert os.path.exists(output_file)
    result_df = pd.read_parquet(output_file)
    assert len(result_df) > 0
    assert "id" in result_df.columns


def test_alifestd_collapse_unifurcations_cli_ignore_topological_sensitivity():
    output_file = (
        "/tmp/hstrat_alifestd_collapse_unifurcations_ignore.csv"  # nosec B108
    )
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_collapse_unifurcations",
            "--ignore-topological-sensitivity",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=f"{assets}/collapse_unifurcations_testphylo.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_collapse_unifurcations_cli_drop_topological_sensitivity():
    output_file = (
        "/tmp/hstrat_alifestd_collapse_unifurcations_drop.csv"  # nosec B108
    )
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_collapse_unifurcations",
            "--drop-topological-sensitivity",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=f"{assets}/collapse_unifurcations_testphylo.csv".encode(),
    )
    assert os.path.exists(output_file)
