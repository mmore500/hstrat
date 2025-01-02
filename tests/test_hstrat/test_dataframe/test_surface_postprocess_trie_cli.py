import os
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


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
            "/tmp/hstrat_surface_postprocess_trie.csv",
        ],
        check=True,
        input="/tmp/hstrat_unpack_surface_reconstruct_.csv".encode(),
    )


def test_surface_postprocess_trie_cli_parquet():
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
            "/tmp/hstrat_surface_postprocess_trie.pqt",
            "--shrink-dtypes",
            "--trie-postprocessor",
            "hstrat.NopTriePostprocessor()",
        ],
        check=True,
        input="/tmp/hstrat_unpack_surface_reconstruct_.pqt".encode(),
    )
