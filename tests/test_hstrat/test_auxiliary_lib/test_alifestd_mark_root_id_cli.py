import os
import pathlib
import subprocess

from packaging.version import parse as parse_version
import pandas as pd
import pytest

pytestmark = pytest.mark.skipif(
    parse_version(pd.__version__) >= parse_version("3"),
    reason="alifestd functions are not compatible with pandas >= 3",
)

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


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
