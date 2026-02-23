import os

import polars as pl
import pytest

from hstrat.dataframe import surface_validate_trie

assets_path = os.path.join(os.path.dirname(__file__), "assets")


# ---------------------------------------------------------------------------
# Smoke / passthrough tests using trie.csv (from packed.csv via pipeline)
# ---------------------------------------------------------------------------


def test_smoke():
    """Validation passes and returns int for well-formed trie."""
    df = pl.read_csv(f"{assets_path}/trie.csv")
    result = surface_validate_trie(df)
    assert isinstance(result, int)
    assert result == 0


def test_smoke_long():
    """Validation passes for late-divergence trie (lrc=47, mrca=55)."""
    df = pl.read_csv(f"{assets_path}/trie_long.csv")
    result = surface_validate_trie(df)
    assert isinstance(result, int)
    assert result == 0


# ---------------------------------------------------------------------------
# Structural validation failures
# ---------------------------------------------------------------------------


def test_missing_deserialization_columns():
    """Raises if dstream metadata columns are absent."""
    df = pl.read_csv(f"{assets_path}/trie.csv")
    stripped = df.drop("data_hex")
    with pytest.raises(ValueError, match="missing downstream metadata columns"):
        surface_validate_trie(stripped)


def test_missing_id_column():
    """Raises if the 'id' column is absent."""
    df = pl.read_csv(f"{assets_path}/trie.csv")
    stripped = df.drop("id")
    with pytest.raises(ValueError, match="missing required column 'id'"):
        surface_validate_trie(stripped)


def test_missing_ancestor_id_column():
    """Raises if the 'ancestor_id' column is absent."""
    df = pl.read_csv(f"{assets_path}/trie.csv")
    stripped = df.drop("ancestor_id")
    with pytest.raises(
        ValueError, match="missing required column 'ancestor_id'"
    ):
        surface_validate_trie(stripped)


def test_non_contiguous_ids():
    """Raises if ids are not contiguous (do not match row indices)."""
    df = pl.read_csv(f"{assets_path}/trie.csv")
    bad = df.with_columns(
        pl.col("id") + 10,
        pl.col("ancestor_id") + 10,
    )
    with pytest.raises(ValueError, match="ids are not contiguous"):
        surface_validate_trie(bad)


def test_no_meta_raises():
    """Trie without dstream metadata columns fails validation."""
    df = pl.read_csv(f"{assets_path}/trie_no_meta.csv")
    with pytest.raises(ValueError, match="missing downstream metadata columns"):
        surface_validate_trie(df)


# ---------------------------------------------------------------------------
# MRCA violation detection using trie_long_invalid.csv
# (lrc=47, corrupted mrca_rank=10 → 47 > 10 → violation)
# ---------------------------------------------------------------------------


def test_violation_detected():
    """Violation is detected when MRCA rank is below last retained commonality."""
    df = pl.read_csv(f"{assets_path}/trie_long_invalid.csv")
    num_violations = surface_validate_trie(
        df, max_num_checks=1_000, max_violations=10
    )
    assert num_violations > 0


def test_violation_returns_count():
    """Returns violation count when max_violations is not exceeded."""
    df = pl.read_csv(f"{assets_path}/trie_long_invalid.csv")
    count = surface_validate_trie(df, max_violations=10)
    assert count >= 1


def test_violation_early_return():
    """Returns early once violations exceed max_violations."""
    df = pl.read_csv(f"{assets_path}/trie_long_invalid.csv")
    max_v = 0
    count = surface_validate_trie(df, max_violations=max_v)
    assert count > max_v


# ---------------------------------------------------------------------------
# Parameter tests
# ---------------------------------------------------------------------------


def test_max_num_checks_zero():
    """With max_num_checks=0, no leaf-pair checks are run; returns 0."""
    df = pl.read_csv(f"{assets_path}/trie.csv")
    result = surface_validate_trie(df, max_num_checks=0)
    assert result == 0


def test_max_num_checks_zero_invalid():
    """With max_num_checks=0, even invalid tries return 0 (no checks done)."""
    df = pl.read_csv(f"{assets_path}/trie_long_invalid.csv")
    result = surface_validate_trie(df, max_num_checks=0)
    assert result == 0


def test_seed_reproducibility():
    """Same seed produces same violation count."""
    df = pl.read_csv(f"{assets_path}/trie_long_invalid.csv")
    count_a = surface_validate_trie(df, seed=42, max_violations=10)
    count_b = surface_validate_trie(df, seed=42, max_violations=10)
    assert count_a == count_b


def test_seed_different():
    """Different seeds may yield different counts (probabilistic)."""
    df = pl.read_csv(f"{assets_path}/trie_long_invalid.csv")
    # Both should still detect violations regardless of seed
    count_0 = surface_validate_trie(df, seed=0, max_violations=10)
    count_1 = surface_validate_trie(df, seed=1, max_violations=10)
    assert count_0 >= 1
    assert count_1 >= 1
