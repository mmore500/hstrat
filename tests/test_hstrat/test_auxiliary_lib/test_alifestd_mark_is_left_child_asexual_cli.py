import os
import pathlib
import subprocess

import pandas as pd

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_mark_is_left_child_asexual_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_mark_is_left_child_asexual",
            "--help",
        ],
        check=True,
    )


def test_alifestd_mark_is_left_child_asexual_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_mark_is_left_child_asexual",
            "--version",
        ],
        check=True,
    )


def test_alifestd_mark_is_left_child_asexual_cli_csv():
    output_file = (
        "/tmp/hstrat_alifestd_mark_is_left_child_asexual.csv"  # nosec B108
    )
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_mark_is_left_child_asexual",
            output_file,
        ],
        check=True,
        input=f"{assets}/example-standard-toy-asexual-bifurcating-phylogeny.csv".encode(),
    )
    assert os.path.exists(output_file)
    result_df = pd.read_csv(output_file)
    assert len(result_df) > 0
    assert "is_left_child" in result_df.columns


def test_alifestd_mark_is_left_child_asexual_cli_parquet():
    output_file = (
        "/tmp/hstrat_alifestd_mark_is_left_child_asexual.pqt"  # nosec B108
    )
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_mark_is_left_child_asexual",
            output_file,
        ],
        check=True,
        input=f"{assets}/example-standard-toy-asexual-bifurcating-phylogeny.csv".encode(),
    )
    assert os.path.exists(output_file)
    result_df = pd.read_parquet(output_file)
    assert len(result_df) > 0
    assert "is_left_child" in result_df.columns
