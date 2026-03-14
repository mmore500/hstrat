import os
import pathlib
import subprocess

import pandas as pd

from ._impl import mark_skipif_pandas_post3

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


@mark_skipif_pandas_post3
def test_alifestd_mark_root_id_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_mark_root_id",
            "--help",
        ],
        check=True,
    )


@mark_skipif_pandas_post3
def test_alifestd_mark_root_id_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_mark_root_id",
            "--version",
        ],
        check=True,
    )


@mark_skipif_pandas_post3
def test_alifestd_mark_root_id_cli_csv():
    output_file = "/tmp/hstrat_alifestd_mark_root_id.csv"  # nosec B108
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_mark_root_id",
            output_file,
        ],
        check=True,
        input=f"{assets}/example-standard-toy-asexual-phylogeny.csv".encode(),
    )
    assert os.path.exists(output_file)
    result_df = pd.read_csv(output_file)
    assert len(result_df) > 0
    assert "root_id" in result_df.columns


@mark_skipif_pandas_post3
def test_alifestd_mark_root_id_cli_parquet():
    output_file = "/tmp/hstrat_alifestd_mark_root_id.pqt"  # nosec B108
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_mark_root_id",
            output_file,
        ],
        check=True,
        input=f"{assets}/example-standard-toy-asexual-phylogeny.csv".encode(),
    )
    assert os.path.exists(output_file)
    result_df = pd.read_parquet(output_file)
    assert len(result_df) > 0
    assert "root_id" in result_df.columns
