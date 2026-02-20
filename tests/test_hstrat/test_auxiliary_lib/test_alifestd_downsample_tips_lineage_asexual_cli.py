import os
import pathlib
import subprocess

import pandas as pd
import pytest

from hstrat._auxiliary_lib import alifestd_to_working_format

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


@pytest.fixture
def working_format_csv(tmp_path):
    """Create a working-format CSV from the NK dataset."""
    df = pd.read_csv(f"{assets}/nk_ecoeaselection.csv")
    wf = alifestd_to_working_format(df)
    path = str(tmp_path / "working_format_input.csv")
    wf.to_csv(path, index=False)
    return path


def test_alifestd_downsample_tips_lineage_asexual_cli_help():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_asexual",
            "--help",
        ],
        check=True,
    )


def test_alifestd_downsample_tips_lineage_asexual_cli_version():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_asexual",
            "--version",
        ],
        check=True,
    )


def test_alifestd_downsample_tips_lineage_asexual_cli_csv(
    tmp_path, working_format_csv
):
    output_file = str(
        tmp_path / "hstrat_alifestd_downsample_tips_lineage_asexual.csv"
    )
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_asexual",
            "-n",
            "1",
            "--criterion-relatedness",
            "origin_time",
            "--criterion-target",
            "origin_time",
            output_file,
        ],
        check=True,
        input=working_format_csv.encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_downsample_tips_lineage_asexual_cli_parquet(
    tmp_path, working_format_csv
):
    output_file = str(
        tmp_path / "hstrat_alifestd_downsample_tips_lineage_asexual.pqt"
    )
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_asexual",
            "-n",
            "1",
            output_file,
        ],
        check=True,
        input=working_format_csv.encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_downsample_tips_lineage_asexual_cli_ignore_topological_sensitivity(  # noqa: E501
    tmp_path, working_format_csv
):
    output_file = str(
        tmp_path
        / "hstrat_alifestd_downsample_tips_lineage_asexual_ignore.csv"
    )
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_asexual",
            "-n",
            "1",
            "--ignore-topological-sensitivity",
            output_file,
        ],
        check=True,
        input=working_format_csv.encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_downsample_tips_lineage_asexual_cli_drop_topological_sensitivity(  # noqa: E501
    tmp_path, working_format_csv
):
    output_file = str(
        tmp_path
        / "hstrat_alifestd_downsample_tips_lineage_asexual_drop.csv"
    )
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_asexual",
            "-n",
            "1",
            "--drop-topological-sensitivity",
            output_file,
        ],
        check=True,
        input=working_format_csv.encode(),
    )
    assert os.path.exists(output_file)
