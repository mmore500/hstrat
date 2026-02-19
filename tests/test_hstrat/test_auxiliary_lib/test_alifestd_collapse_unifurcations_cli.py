import os
import pathlib
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_collapse_unifurcations_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_collapse_unifurcations",
            "--help",
        ],
        check=True,
    )


def test_alifestd_collapse_unifurcations_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_collapse_unifurcations",
            "--version",
        ],
        check=True,
    )


def test_alifestd_collapse_unifurcations_cli_csv():
    output_file = "/tmp/hstrat_alifestd_collapse_unifurcations.csv"
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_collapse_unifurcations",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=f"{assets}/collapse_unifurcations_testphylo.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_collapse_unifurcations_cli_parquet():
    output_file = "/tmp/hstrat_alifestd_collapse_unifurcations.pqt"
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_collapse_unifurcations",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=f"{assets}/collapse_unifurcations_testphylo.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_collapse_unifurcations_cli_ignore_topological_sensitivity():
    output_file = "/tmp/hstrat_alifestd_collapse_unifurcations_ignore.csv"
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_collapse_unifurcations",
            "--ignore-topological-sensitivity",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=f"{assets}/collapse_unifurcations_testphylo.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_collapse_unifurcations_cli_drop_topological_sensitivity():
    output_file = "/tmp/hstrat_alifestd_collapse_unifurcations_drop.csv"
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_collapse_unifurcations",
            "--drop-topological-sensitivity",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=f"{assets}/collapse_unifurcations_testphylo.csv".encode(),
    )
    assert os.path.exists(output_file)
