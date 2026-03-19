import os
import pathlib
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_mark_leaves_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_mark_leaves",
            "--help",
        ],
        check=True,
    )


def test_alifestd_mark_leaves_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_mark_leaves",
            "--version",
        ],
        check=True,
    )


def test_alifestd_mark_leaves_cli_csv():
    output_file = "/tmp/hstrat_alifestd_mark_leaves.csv"
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_mark_leaves",
            output_file,
        ],
        check=True,
        input=f"{assets}/example-standard-toy-asexual-phylogeny.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_mark_leaves_cli_parquet():
    output_file = "/tmp/hstrat_alifestd_mark_leaves.pqt"
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_mark_leaves",
            output_file,
        ],
        check=True,
        input=f"{assets}/example-standard-toy-asexual-phylogeny.csv".encode(),
    )
    assert os.path.exists(output_file)
