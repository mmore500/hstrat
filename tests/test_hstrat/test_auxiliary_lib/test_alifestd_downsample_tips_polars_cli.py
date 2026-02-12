import os
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


def test_alifestd_downsample_tips_polars_cli_csv(tmp_path):
    output_file = str(tmp_path / "hstrat_alifestd_downsample_tips_polars.csv")
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


def test_alifestd_downsample_tips_polars_cli_empty(tmp_path):
    output_file = str(tmp_path / "hstrat_alifestd_downsample_tips_polars.csv")
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
