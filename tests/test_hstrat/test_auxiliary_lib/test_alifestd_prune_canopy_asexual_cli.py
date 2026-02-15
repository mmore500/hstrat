import os
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_prune_canopy_asexual_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_prune_canopy_asexual",
            "--help",
        ],
        check=True,
    )


def test_alifestd_prune_canopy_asexual_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_prune_canopy_asexual",
            "--version",
        ],
        check=True,
    )


def test_alifestd_prune_canopy_asexual_cli_csv(tmp_path):
    output_file = str(
        tmp_path / "hstrat_alifestd_prune_canopy_asexual.csv"
    )
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_prune_canopy_asexual",
            "-n",
            "1",
            "--criterion",
            "id",
            output_file,
        ],
        check=True,
        input=f"{assets}/example-standard-toy-asexual-phylogeny.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_prune_canopy_asexual_cli_parquet(tmp_path):
    output_file = str(
        tmp_path / "hstrat_alifestd_prune_canopy_asexual.pqt"
    )
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_prune_canopy_asexual",
            "-n",
            "1",
            "--criterion",
            "id",
            output_file,
        ],
        check=True,
        input=f"{assets}/example-standard-toy-asexual-phylogeny.csv".encode(),
    )
    assert os.path.exists(output_file)
