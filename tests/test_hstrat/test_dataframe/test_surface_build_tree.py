import os
import re

from phyloframe import legacy as pfl
import polars as pl
import pytest

from hstrat.dataframe import surface_build_tree
from hstrat.dataframe.surface_build_tree import _create_parser
from hstrat.phylogenetic_inference.tree.trie_postprocess import (
    AssignOriginTimeNodeRankTriePostprocessor,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def test_smoke():
    df = pl.read_csv(f"{assets_path}/packed.csv")
    res = surface_build_tree(
        df,
        collapse_unif_freq=0,
        trie_postprocessor=AssignOriginTimeNodeRankTriePostprocessor(
            t0="dstream_S",
        ),
    )
    assert "origin_time" in res.columns
    assert len(df) <= len(res)
    assert pfl.alifestd_validate(
        pfl.alifestd_try_add_ancestor_list_col(res.to_pandas()),
    )
    assert pfl.alifestd_is_chronologically_ordered(res.to_pandas())


def test_shuffle_over_same_T_seed():
    """Smoke test: shuffle_over_same_T_seed produces a valid phylogeny."""
    df = pl.read_csv(f"{assets_path}/packed.csv")
    res = surface_build_tree(
        df,
        collapse_unif_freq=0,
        shuffle_over_same_T_seed=42,
        trie_postprocessor=AssignOriginTimeNodeRankTriePostprocessor(
            t0="dstream_S",
        ),
    )
    assert "origin_time" in res.columns
    assert len(df) <= len(res)
    assert pfl.alifestd_validate(
        pfl.alifestd_try_add_ancestor_list_col(res.to_pandas()),
    )
    assert pfl.alifestd_is_chronologically_ordered(res.to_pandas())


def test_drop_dstream_metadata_default():
    """Default behavior (None) should drop dstream/downstream columns."""
    df = pl.read_csv(f"{assets_path}/packed.csv")
    res = surface_build_tree(df, collapse_unif_freq=0)
    # only dstream_data_id and dstream_S should survive (dstream_rank
    # is consumed by postprocess_trie)
    assert "dstream_data_id" in res.columns


def test_drop_dstream_metadata_true_raises():
    """Passing drop_dstream_metadata=True should raise NotImplementedError."""
    df = pl.read_csv(f"{assets_path}/packed.csv")
    with pytest.raises(NotImplementedError):
        surface_build_tree(
            df, collapse_unif_freq=0, drop_dstream_metadata=True
        )


def test_drop_dstream_metadata_false():
    """Passing drop_dstream_metadata=False should retain more dstream columns
    than the default behavior."""
    df = pl.read_csv(f"{assets_path}/packed.csv")
    res_default = surface_build_tree(df, collapse_unif_freq=0)
    res_no_drop = surface_build_tree(
        df,
        collapse_unif_freq=0,
        drop_dstream_metadata=False,
    )
    assert len(res_no_drop) > 0
    default_dstream_cols = {
        c
        for c in res_default.columns
        if re.match(r"^dstream_", c) or re.match(r"^downstream_", c)
    }
    no_drop_dstream_cols = {
        c
        for c in res_no_drop.columns
        if re.match(r"^dstream_", c) or re.match(r"^downstream_", c)
    }
    # --no-drop-dstream-metadata should retain at least as many columns
    assert default_dstream_cols <= no_drop_dstream_cols
    # and should have strictly more dstream/downstream columns than default
    assert len(no_drop_dstream_cols) > len(default_dstream_cols)


def test_drop_dstream_metadata_false_preserves_dstream_rank():
    """Passing drop_dstream_metadata=False should preserve dstream_rank
    through both surface_unpack_reconstruct and surface_postprocess_trie."""
    df = pl.read_csv(f"{assets_path}/packed.csv")
    res_default = surface_build_tree(df, collapse_unif_freq=0)
    res_no_drop = surface_build_tree(
        df,
        collapse_unif_freq=0,
        drop_dstream_metadata=False,
    )
    # dstream_rank should be dropped by default
    assert "dstream_rank" not in res_default.columns
    # dstream_rank should be preserved when drop_dstream_metadata=False
    assert "dstream_rank" in res_no_drop.columns
    assert res_no_drop["dstream_rank"].null_count() < len(res_no_drop)


def test_parser_no_prefix_matching_drop():
    """Regression: --drop must not prefix-match --drop-dstream-metadata."""
    parser = _create_parser()
    args, remaining = parser.parse_known_args(
        [
            "--no-drop-dstream-metadata",
            "--drop",
            "awoo",
            "/dev/null",
        ],
    )
    assert args.drop_dstream_metadata is False
    assert "--drop" in remaining
    assert "awoo" in remaining


def _get_full_schema():
    """Get expected output schema from a known-good two-genome run."""
    df = pl.read_csv(f"{assets_path}/packed.csv")
    return surface_build_tree(df, collapse_unif_freq=0).schema


def test_empty():
    """Regression: empty genome set should produce an empty phylogeny without
    crashing, with the same columns and types as a non-empty result."""
    df = pl.read_csv(f"{assets_path}/packed.csv").head(0)
    res = surface_build_tree(df)
    assert len(res) == 0
    full_schema = _get_full_schema()
    assert set(res.schema.names()) == set(full_schema.names())
    for col in full_schema.names():
        assert (
            res.schema[col] == full_schema[col]
        ), f"type mismatch for {col}: {res.schema[col]} != {full_schema[col]}"


def test_single_genome():
    """Regression: a single genome should not crash."""
    df = pl.read_csv(f"{assets_path}/packed.csv").head(1)
    res = surface_build_tree(
        df,
        collapse_unif_freq=0,
        trie_postprocessor=AssignOriginTimeNodeRankTriePostprocessor(
            t0="dstream_S",
        ),
    )
    # single genome may produce empty tree after trunk deletion
    assert isinstance(res, pl.DataFrame)
    if len(res) == 0:
        full_schema = _get_full_schema()
        assert set(res.schema.names()) == set(full_schema.names())
        for col in full_schema.names():
            assert res.schema[col] == full_schema[col], (
                f"type mismatch for {col}: "
                f"{res.schema[col]} != {full_schema[col]}"
            )


def test_single_genome_no_delete_trunk():
    """Regression: a single genome without trunk deletion should produce a
    valid phylogeny."""
    df = pl.read_csv(f"{assets_path}/packed.csv").head(1)
    res = surface_build_tree(
        df,
        collapse_unif_freq=0,
        delete_trunk=False,
        trie_postprocessor=AssignOriginTimeNodeRankTriePostprocessor(
            t0="dstream_S",
        ),
    )
    assert len(res) >= 1
    assert pfl.alifestd_validate(
        pfl.alifestd_try_add_ancestor_list_col(res.to_pandas()),
    )
    assert pfl.alifestd_is_chronologically_ordered(res.to_pandas())
