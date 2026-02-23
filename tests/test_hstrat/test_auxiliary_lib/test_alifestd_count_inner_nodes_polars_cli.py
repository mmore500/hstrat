import os
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_count_inner_nodes_polars_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_count_inner_nodes_polars",
            "--help",
        ],
        check=True,
    )


def test_alifestd_count_inner_nodes_polars_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_count_inner_nodes_polars",
            "--version",
        ],
        check=True,
    )


def test_alifestd_count_inner_nodes_polars_cli_csv():
    cmd = [
        "python3",
        "-m",
        "hstrat._auxiliary_lib._alifestd_count_inner_nodes_polars",
        f"{assets}/trunktestphylo.csv",
    ]
    result = subprocess.run(
        cmd, capture_output=True, check=True, text=True
    )  # nosec B603
    count = int(result.stdout.strip())
    assert count >= 0
