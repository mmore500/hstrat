import os

import polars as pl
import pytest

from hstrat.dataframe import (
    alifestd_validate_trie,
    surface_unpack_reconstruct,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def test_smoke():
    df = pl.read_csv(f"{assets_path}/packed.csv")
    raw = surface_unpack_reconstruct(df, drop_dstream_metadata=False)
    result = alifestd_validate_trie(raw)
    assert result.shape == raw.shape


def test_passthrough():
    df = pl.read_csv(f"{assets_path}/packed.csv")
    raw = surface_unpack_reconstruct(df, drop_dstream_metadata=False)
    result = alifestd_validate_trie(raw)
    assert result.equals(raw)


def test_missing_deserialization_columns():
    df = pl.read_csv(f"{assets_path}/packed.csv")
    raw = surface_unpack_reconstruct(df, drop_dstream_metadata=False)
    stripped = raw.drop("data_hex")
    with pytest.raises(ValueError, match="missing deserialization columns"):
        alifestd_validate_trie(stripped)


def test_missing_id_column():
    df = pl.read_csv(f"{assets_path}/packed.csv")
    raw = surface_unpack_reconstruct(df, drop_dstream_metadata=False)
    stripped = raw.drop("id")
    with pytest.raises(ValueError, match="missing required column 'id'"):
        alifestd_validate_trie(stripped)


def test_missing_ancestor_id_column():
    df = pl.read_csv(f"{assets_path}/packed.csv")
    raw = surface_unpack_reconstruct(df, drop_dstream_metadata=False)
    stripped = raw.drop("ancestor_id")
    with pytest.raises(
        ValueError, match="missing required column 'ancestor_id'"
    ):
        alifestd_validate_trie(stripped)


def test_non_contiguous_ids():
    df = pl.read_csv(f"{assets_path}/packed.csv")
    raw = surface_unpack_reconstruct(df, drop_dstream_metadata=False)
    # shift ids to make non-contiguous
    bad = raw.with_columns(
        pl.col("id") + 10,
        pl.col("ancestor_id") + 10,
    )
    with pytest.raises(ValueError, match="ids are not contiguous"):
        alifestd_validate_trie(bad)


def test_default_drop_metadata_fails():
    """Validate that default metadata dropping causes validation failure."""
    df = pl.read_csv(f"{assets_path}/packed.csv")
    raw = surface_unpack_reconstruct(df)  # default drops dstream columns
    with pytest.raises(ValueError, match="missing deserialization columns"):
        alifestd_validate_trie(raw)
