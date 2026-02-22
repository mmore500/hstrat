import os
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_surface_validate_trie_cli_help():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_validate_trie",
            "--help",
        ],
        check=True,
    )


def test_surface_validate_trie_cli_version():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_validate_trie",
            "--version",
        ],
        check=True,
    )


def test_surface_validate_trie_cli_csv():
    """Validates a well-formed trie CSV and prints violation count."""
    result = subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_validate_trie",
            f"{assets}/trie.csv",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "0"


def test_surface_validate_trie_cli_parquet():
    """Validates a well-formed trie from a Parquet file."""
    trie_pqt = "/tmp/hstrat_validate_trie_input.pqt"  # nosec B108
    import polars as pl

    pl.read_csv(f"{assets}/trie.csv").write_parquet(trie_pqt)

    result = subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_validate_trie",
            trie_pqt,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "0"


def test_surface_validate_trie_cli_long():
    """Validates a late-divergence trie (lrc=47, mrca=55)."""
    result = subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_validate_trie",
            f"{assets}/trie_long.csv",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "0"


def test_surface_validate_trie_cli_fails_without_metadata():
    """CLI exits non-zero when dstream metadata columns are absent."""
    result = subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_validate_trie",
            f"{assets}/trie_no_meta.csv",
        ],
    )
    assert result.returncode != 0


def test_surface_validate_trie_cli_fails_on_invalid_trie():
    """CLI exits non-zero when trie has MRCA rank violations."""
    result = subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_validate_trie",
            f"{assets}/trie_long_invalid.csv",
            "--max-violations",
            "0",
        ],
    )
    assert result.returncode != 0


def test_surface_validate_trie_cli_max_num_checks_zero():
    """With --max-num-checks 0, no leaf-pair checks run; always passes."""
    result = subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_validate_trie",
            f"{assets}/trie_long_invalid.csv",
            "--max-num-checks",
            "0",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "0"


def test_surface_validate_trie_cli_max_violations():
    """--max-violations controls the threshold before exit-on-error."""
    result = subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_validate_trie",
            f"{assets}/trie_long_invalid.csv",
            "--max-violations",
            "9999",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    # violation count is printed even when within tolerance
    assert result.stdout.strip().isdigit()


def test_surface_validate_trie_cli_seed():
    """--seed flag is accepted and produces reproducible results."""
    results = []
    for _ in range(2):
        r = subprocess.run(
            [
                "python3",
                "-m",
                "hstrat.dataframe.surface_validate_trie",
                f"{assets}/trie.csv",
                "--seed",
                "42",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        results.append(r.stdout.strip())
    assert results[0] == results[1]
