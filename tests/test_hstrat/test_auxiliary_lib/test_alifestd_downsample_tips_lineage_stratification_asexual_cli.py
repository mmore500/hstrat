import os
import pathlib
import subprocess

import pandas as pd

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_downsample_tips_lineage_stratification_asexual_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_stratification_asexual",
            "--help",
        ],
        check=True,
    )


def test_alifestd_downsample_tips_lineage_stratification_asexual_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_stratification_asexual",
            "--version",
        ],
        check=True,
    )


def test_alifestd_downsample_tips_lineage_stratification_asexual_cli_csv(
    tmp_path,
):
    output_file = str(
        tmp_path
        / "hstrat_alifestd_downsample_tips_lineage_stratification_asexual.csv"
    )
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_stratification_asexual",
            "-n",
            "5",
            output_file,
        ],
        check=True,
        input=f"{assets}/nk_ecoeaselection-workingformat.csv".encode(),
    )
    assert os.path.exists(output_file)
    result_df = pd.read_csv(output_file)
    assert len(result_df) > 0
    assert "id" in result_df.columns


def test_alifestd_downsample_tips_lineage_stratification_asexual_cli_parquet(
    tmp_path,
):
    output_file = str(
        tmp_path
        / "hstrat_alifestd_downsample_tips_lineage_stratification_asexual.pqt"
    )
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_stratification_asexual",
            "-n",
            "5",
            output_file,
        ],
        check=True,
        input=f"{assets}/nk_ecoeaselection-workingformat.csv".encode(),
    )
    assert os.path.exists(output_file)
    result_df = pd.read_parquet(output_file)
    assert len(result_df) > 0
    assert "id" in result_df.columns


def test_alifestd_downsample_tips_lineage_stratification_asexual_cli_ignore_topological_sensitivity():  # noqa: E501
    output_file = "/tmp/hstrat_alifestd_downsample_tips_lineage_stratification_asexual_ignore.csv"  # nosec B108
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_stratification_asexual",
            "-n",
            "5",
            "--ignore-topological-sensitivity",
            output_file,
        ],
        check=True,
        input=f"{assets}/nk_ecoeaselection-workingformat.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_downsample_tips_lineage_stratification_asexual_cli_drop_topological_sensitivity():
    output_file = "/tmp/hstrat_alifestd_downsample_tips_lineage_stratification_asexual_drop.csv"  # nosec B108
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_stratification_asexual",
            "-n",
            "5",
            "--drop-topological-sensitivity",
            output_file,
        ],
        check=True,
        input=f"{assets}/nk_ecoeaselection-workingformat.csv".encode(),
    )
    assert os.path.exists(output_file)
