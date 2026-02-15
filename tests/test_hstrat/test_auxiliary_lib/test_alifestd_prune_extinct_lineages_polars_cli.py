import os
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_prune_extinct_lineages_polars_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_prune_extinct_lineages_polars",
            "--help",
        ],
        check=True,
    )


def test_alifestd_prune_extinct_lineages_polars_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_prune_extinct_lineages_polars",
            "--version",
        ],
        check=True,
    )


def test_alifestd_prune_extinct_lineages_polars_cli_csv(tmp_path):
    output_file = str(
        tmp_path / "hstrat_alifestd_prune_extinct_lineages_polars.csv"
    )
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_prune_extinct_lineages_polars",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=f"{assets}/prunetestphylo.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_prune_extinct_lineages_polars_cli_empty(tmp_path):
    output_file = str(
        tmp_path / "hstrat_alifestd_prune_extinct_lineages_polars.csv"
    )
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_prune_extinct_lineages_polars",
            output_file,
        ],
        check=True,
        input=f"{assets}/empty.csv".encode(),
    )
    assert os.path.exists(output_file)
