import os
import pathlib
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_downsample_canopy_polars_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_canopy_polars",
            "--help",
        ],
        check=True,
    )


def test_alifestd_downsample_canopy_polars_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_canopy_polars",
            "--version",
        ],
        check=True,
    )


def test_alifestd_downsample_canopy_polars_cli_csv(tmp_path):
    output_file = str(
        tmp_path / "hstrat_alifestd_downsample_canopy_polars.csv"
    )
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_canopy_polars",
            "-n",
            "4",
            "--criterion",
            "id",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=f"{assets}/trunktestphylo.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_downsample_canopy_polars_cli_empty(tmp_path):
    output_file = str(
        tmp_path / "hstrat_alifestd_downsample_canopy_polars.csv"
    )
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_canopy_polars",
            "-n",
            "10",
            "--criterion",
            "id",
            output_file,
        ],
        check=True,
        input=f"{assets}/empty.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_downsample_canopy_polars_cli_ignore_topological_sensitivity():  # noqa: E501
    output_file = "/tmp/hstrat_alifestd_downsample_canopy_polars_ignore.csv"  # nosec B108
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_canopy_polars",
            "-n",
            "4",
            "--criterion",
            "id",
            "--ignore-topological-sensitivity",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=f"{assets}/trunktestphylo.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_downsample_canopy_polars_cli_drop_topological_sensitivity():
    output_file = (
        "/tmp/hstrat_alifestd_downsample_canopy_polars_drop.csv"  # nosec B108
    )
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_canopy_polars",
            "-n",
            "4",
            "--criterion",
            "id",
            "--drop-topological-sensitivity",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=f"{assets}/trunktestphylo.csv".encode(),
    )
    assert os.path.exists(output_file)
