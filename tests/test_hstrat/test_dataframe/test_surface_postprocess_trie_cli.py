import os
import pathlib
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_surface_postprocess_trie_cli_help():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_postprocess_trie",
            "--help",
        ],
        check=True,
    )


def test_surface_postprocess_trie_cli_version():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_postprocess_trie",
            "--version",
        ],
        check=True,
    )


def test_surface_postprocess_trie_cli_csv():
    output_file = "/tmp/hstrat_surface_postprocess_trie.csv"
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_unpack_reconstruct",
            "/tmp/hstrat_unpack_surface_reconstruct_.csv",
        ],
        check=True,
        input=f"{assets}/packed.csv".encode(),
    )
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_postprocess_trie",
            output_file,
        ],
        check=True,
        input="/tmp/hstrat_unpack_surface_reconstruct_.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_surface_postprocess_trie_cli_parquet():
    output_file = "/tmp/hstrat_surface_postprocess_trie.pqt"
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_unpack_reconstruct",
            "/tmp/hstrat_unpack_surface_reconstruct_.pqt",
            "--shrink-dtypes",
            "--exploded-slice-size",
            "50_000_000",
        ],
        check=True,
        input=f"{assets}/packed.csv".encode(),
    )
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_postprocess_trie",
            output_file,
            "--shrink-dtypes",
            "--trie-postprocessor",
            "hstrat.NopTriePostprocessor()",
        ],
        check=True,
        input="/tmp/hstrat_unpack_surface_reconstruct_.pqt".encode(),
    )
    assert os.path.exists(output_file)
