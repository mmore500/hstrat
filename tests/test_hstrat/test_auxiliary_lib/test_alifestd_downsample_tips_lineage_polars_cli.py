import os
import pathlib
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_downsample_tips_lineage_polars_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_polars",
            "--help",
        ],
        check=True,
    )


def test_alifestd_downsample_tips_lineage_polars_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_polars",
            "--version",
        ],
        check=True,
    )


def test_alifestd_downsample_tips_lineage_polars_cli_csv():
    output_file = (
        "/tmp/hstrat_alifestd_downsample_tips_lineage_polars.csv"  # nosec B108
    )
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_polars",
            "-n",
            "1",
            "--criterion-delta",
            "origin_time",
            "--criterion-target",
            "origin_time",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=(f"{assets}/nk_ecoeaselection-workingformat.csv".encode()),
    )
    assert os.path.exists(output_file)


def test_alifestd_downsample_tips_lineage_polars_cli_parquet():
    output_file = (
        "/tmp/hstrat_alifestd_downsample_tips_lineage_polars.pqt"  # nosec B108
    )
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_polars",
            "-n",
            "1",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=(f"{assets}/nk_ecoeaselection-workingformat.csv".encode()),
    )
    assert os.path.exists(output_file)


def test_alifestd_downsample_tips_lineage_polars_cli_ignore_topological_sensitivity():  # noqa: E501
    output_file = "/tmp/hstrat_alifestd_downsample_tips_lineage_polars_ignore.csv"  # nosec B108
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_polars",
            "-n",
            "1",
            "--ignore-topological-sensitivity",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=(f"{assets}/nk_ecoeaselection-workingformat.csv".encode()),
    )
    assert os.path.exists(output_file)


def test_alifestd_downsample_tips_lineage_polars_cli_drop_topological_sensitivity():  # noqa: E501
    output_file = "/tmp/hstrat_alifestd_downsample_tips_lineage_polars_drop.csv"  # nosec B108
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_polars",
            "-n",
            "1",
            "--drop-topological-sensitivity",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=(f"{assets}/nk_ecoeaselection-workingformat.csv".encode()),
    )
    assert os.path.exists(output_file)
