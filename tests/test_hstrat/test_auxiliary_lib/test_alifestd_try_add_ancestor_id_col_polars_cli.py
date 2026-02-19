import os
import pathlib
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_try_add_ancestor_id_col_polars_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_try_add_ancestor_id_col_polars",
            "--help",
        ],
        check=True,
    )


def test_alifestd_try_add_ancestor_id_col_polars_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_try_add_ancestor_id_col_polars",
            "--version",
        ],
        check=True,
    )


def test_alifestd_try_add_ancestor_id_col_polars_cli_csv():
    output_file = (
        "/tmp/hstrat_alifestd_try_add_ancestor_id_col_polars.csv"  # nosec B108
    )
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_try_add_ancestor_id_col_polars",
            output_file,
        ],
        check=True,
        input=f"{assets}/nk_ecoeaselection.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_try_add_ancestor_id_col_polars_cli_parquet():
    output_file = (
        "/tmp/hstrat_alifestd_try_add_ancestor_id_col_polars.pqt"  # nosec B108
    )
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_try_add_ancestor_id_col_polars",
            output_file,
        ],
        check=True,
        input=f"{assets}/nk_ecoeaselection.csv".encode(),
    )
    assert os.path.exists(output_file)
