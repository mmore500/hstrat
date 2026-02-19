import os
import pathlib
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_downsample_tips_polars_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_polars",
            "--help",
        ],
        check=True,
    )


def test_alifestd_downsample_tips_polars_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_polars",
            "--version",
        ],
        check=True,
    )


def test_alifestd_downsample_tips_polars_cli_csv():
    output_file = "/tmp/hstrat_alifestd_downsample_tips_polars.csv"
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_polars",
            "-n",
            "4",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=f"{assets}/trunktestphylo.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_downsample_tips_polars_cli_empty():
    output_file = "/tmp/hstrat_alifestd_downsample_tips_polars_empty.csv"
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_polars",
            "-n",
            "10",
            output_file,
        ],
        check=True,
        input=f"{assets}/empty.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_downsample_tips_polars_cli_ignore_topological_sensitivity():
    output_file = (
        "/tmp/hstrat_alifestd_downsample_tips_polars_ignore.csv"
    )
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_polars",
            "-n",
            "4",
            "--ignore-topological-sensitivity",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=f"{assets}/trunktestphylo.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_downsample_tips_polars_cli_drop_topological_sensitivity():
    output_file = (
        "/tmp/hstrat_alifestd_downsample_tips_polars_drop.csv"
    )
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_downsample_tips_polars",
            "-n",
            "4",
            "--drop-topological-sensitivity",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=f"{assets}/trunktestphylo.csv".encode(),
    )
    assert os.path.exists(output_file)
