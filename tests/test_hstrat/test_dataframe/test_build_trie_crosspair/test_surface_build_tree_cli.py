import os
import pathlib
import subprocess

import polars as pl

assets = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets"
)


def test_surface_build_tree_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat.dataframe.build_trie_crosspair.surface_build_tree",
            "--help",
        ],
        check=True,
    )


def test_surface_build_tree_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat.dataframe.build_trie_crosspair.surface_build_tree",
            "--version",
        ],
        check=True,
    )


def test_surface_build_tree_cli_csv():
    output_file = (
        "/tmp/hstrat_build_trie_crosspair_surface_build_tree.csv"  # nosec B108
    )
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat.dataframe.build_trie_crosspair.surface_build_tree",
            output_file,
        ],
        check=True,
        input=f"{assets}/packed.csv".encode(),
    )
    assert os.path.exists(output_file)
    df = pl.read_csv(output_file)
    assert {"id", "ancestor_id", "origin_time"} <= {*df.columns}
