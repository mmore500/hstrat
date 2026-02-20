import os
import pathlib
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_calc_mrca_id_vector_asexual_polars_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_calc_mrca_id_vector_asexual_polars",
            "--help",
        ],
        check=True,
    )


def test_alifestd_calc_mrca_id_vector_asexual_polars_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_calc_mrca_id_vector_asexual_polars",
            "--version",
        ],
        check=True,
    )


def test_alifestd_calc_mrca_id_vector_asexual_polars_cli_csv():
    output_file = "/tmp/hstrat_alifestd_calc_mrca_id_vector_asexual_polars.csv"
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_calc_mrca_id_vector_asexual_polars",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=f"{assets}/trunktestphylo.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_calc_mrca_id_vector_asexual_polars_cli_csv_target():
    output_file = (
        "/tmp/hstrat_alifestd_calc_mrca_id_vector_asexual_polars_t1.csv"
    )
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_calc_mrca_id_vector_asexual_polars",
            "--target-id",
            "1",
            "--eager-write",
            output_file,
        ],
        check=True,
        input=f"{assets}/trunktestphylo.csv".encode(),
    )
    assert os.path.exists(output_file)
