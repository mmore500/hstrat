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


def test_alifestd_splay_polytomies_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_splay_polytomies",
            "--help",
        ],
        check=True,
    )


def test_alifestd_splay_polytomies_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_splay_polytomies",
            "--version",
        ],
        check=True,
    )


def test_alifestd_splay_polytomies_cli_csv():
    output_file = "/tmp/hstrat_alifestd_splay_polytomies.csv"  # nosec B108
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_splay_polytomies",
            output_file,
        ],
        check=True,
        input=f"{assets}/nk_ecoeaselection.csv".encode(),
    )
    assert os.path.exists(output_file)
    result_df = pd.read_csv(output_file)
    assert len(result_df) > 0
    assert "id" in result_df.columns


def test_alifestd_splay_polytomies_cli_parquet():
    output_file = "/tmp/hstrat_alifestd_splay_polytomies.pqt"  # nosec B108
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_splay_polytomies",
            output_file,
        ],
        check=True,
        input=f"{assets}/nk_ecoeaselection.csv".encode(),
    )
    assert os.path.exists(output_file)
    result_df = pd.read_parquet(output_file)
    assert len(result_df) > 0
    assert "id" in result_df.columns
