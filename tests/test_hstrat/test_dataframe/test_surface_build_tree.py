import os

from phyloframe import legacy as pfl
import polars as pl

from hstrat.dataframe import surface_build_tree
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


def test_empty():
    """Regression: empty genome set should produce an empty phylogeny without
    crashing."""
    df = pl.read_csv(f"{assets_path}/packed.csv").head(0)
    res = surface_build_tree(df)
    assert len(res) == 0


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
