import os
import pathlib
import subprocess

import polars as pl

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_surface_unpack_reconstruct_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_unpack_reconstruct",
            "--help",
        ],
        check=True,
    )


def test_surface_unpack_reconstruct_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_unpack_reconstruct",
            "--version",
        ],
        check=True,
    )


def test_surface_unpack_reconstruct_cli_csv():
    output_file = "/tmp/hstrat_unpack_surface_reconstruct.csv"  # nosec B108
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_unpack_reconstruct",
            output_file,
        ],
        check=True,
        input=f"{assets}/packed.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_surface_unpack_reconstruct_cli_parquet():
    output_file = "/tmp/hstrat_unpack_surface_reconstruct.pqt"  # nosec B108
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_unpack_reconstruct",
            output_file,
            "--shrink-dtypes",
            "--exploded-slice-size",
            "50_000_000",
        ],
        check=True,
        input=f"{assets}/packed.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_surface_unpack_reconstruct_cli_no_drop_dstream_metadata():
    output_file = (
        "/tmp/hstrat_unpack_surface_reconstruct_no_drop.pqt"  # nosec B108
    )
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_unpack_reconstruct",
            output_file,
            "--no-drop-dstream-metadata",
        ],
        check=True,
        input=f"{assets}/packed.csv".encode(),
    )
    assert os.path.exists(output_file)
    res = pl.read_parquet(output_file)
    dstream_cols = [c for c in res.columns if c.startswith("dstream_")]
    # should have more than just dstream_data_id and dstream_S
    assert len(dstream_cols) > 2


def test_surface_unpack_reconstruct_cli_drop_with_no_drop_dstream_metadata():
    """Regression: --drop must not prefix-match --drop-dstream-metadata.

    Before allow_abbrev=False, argparse would prefix-match the joinem
    --drop flag to the hstrat --drop-dstream-metadata flag when
    parse_known_args was called (before joinem registered --drop).
    This caused a conflict with --no-drop-dstream-metadata on the same
    command line.
    """
    output_file = (
        "/tmp/hstrat_unpack_surface_reconstruct_drop_col.pqt"  # nosec B108
    )
    pathlib.Path(output_file).unlink(missing_ok=True)
    result = subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_unpack_reconstruct",
            output_file,
            "--no-drop-dstream-metadata",
            "--drop",
            "awoo",
        ],
        check=True,
        input=f"{assets}/packed.csv".encode(),
    )
    assert result.returncode == 0
    assert os.path.exists(output_file)
    res = pl.read_parquet(output_file)
    assert "awoo" not in res.columns
    dstream_cols = [c for c in res.columns if c.startswith("dstream_")]
    # --no-drop-dstream-metadata should retain dstream metadata columns
    assert len(dstream_cols) > 2


def test_surface_unpack_reconstruct_cli_check_trie_invariant_freq():
    """Smoke test for --check-trie-invariant-freq flag."""
    output_file = (
        "/tmp/hstrat_unpack_surface_reconstruct_invariant.csv"  # nosec B108
    )
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_unpack_reconstruct",
            output_file,
            "--check-trie-invariant-freq",
            "1",
        ],
        check=True,
        input=f"{assets}/packed.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_surface_unpack_reconstruct_cli_check_trie_invariant_freq_zero():
    """Smoke test for --check-trie-invariant-freq=0 (disabled, default)."""
    output_file = (
        "/tmp/hstrat_unpack_surface_reconstruct_invariant0.csv"  # nosec B108
    )
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_unpack_reconstruct",
            output_file,
            "--check-trie-invariant-freq",
            "0",
        ],
        check=True,
        input=f"{assets}/packed.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_surface_unpack_reconstruct_cli_mp_pool_size():
    output_file = (
        "/tmp/hstrat_unpack_surface_reconstruct_pool.csv"  # nosec B108
    )
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_unpack_reconstruct",
            output_file,
            "--mp-pool-size",
            "2",
        ],
        check=True,
        input=f"{assets}/packed.csv".encode(),
    )
    assert os.path.exists(output_file)


def test_surface_unpack_reconstruct_cli_drop_dstream_metadata_fails():
    output_file = (
        "/tmp/hstrat_unpack_surface_reconstruct_drop.pqt"  # nosec B108
    )
    pathlib.Path(output_file).unlink(missing_ok=True)
    result = subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_unpack_reconstruct",
            output_file,
            "--drop-dstream-metadata",
        ],
        input=f"{assets}/packed.csv".encode(),
    )
    assert result.returncode != 0
