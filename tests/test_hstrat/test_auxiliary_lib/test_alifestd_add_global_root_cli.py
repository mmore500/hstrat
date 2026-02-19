import os
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_add_global_root_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_add_global_root",
            "--help",
        ],
        check=True,
    )


def test_alifestd_add_global_root_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_add_global_root",
            "--version",
        ],
        check=True,
    )


def test_alifestd_add_global_root_cli_csv(tmp_path):
    output_file = str(tmp_path / "hstrat_alifestd_add_global_root.csv")
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_add_global_root",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=f"{assets}/example-standard-toy-asexual-phylogeny.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_add_global_root_cli_parquet(tmp_path):
    output_file = str(tmp_path / "hstrat_alifestd_add_global_root.pqt")
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_add_global_root",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=f"{assets}/example-standard-toy-asexual-phylogeny.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_add_global_root_cli_ignore_topological_sensitivity(
    tmp_path,
):
    output_file = str(tmp_path / "output.csv")
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_add_global_root",
            "--ignore-topological-sensitivity",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=f"{assets}/example-standard-toy-asexual-phylogeny.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_add_global_root_cli_drop_topological_sensitivity(tmp_path):
    output_file = str(tmp_path / "output.csv")
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_add_global_root",
            "--drop-topological-sensitivity",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=f"{assets}/example-standard-toy-asexual-phylogeny.csv".encode(),
    )
    assert os.path.exists(output_file)
