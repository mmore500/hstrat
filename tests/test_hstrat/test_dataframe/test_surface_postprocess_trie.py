import os

import polars as pl

from hstrat._auxiliary_lib import (
    alifestd_is_chronologically_ordered,
    alifestd_try_add_ancestor_list_col,
    alifestd_validate,
)
from hstrat.dataframe import (
    surface_postprocess_trie,
    surface_unpack_reconstruct,
)
from hstrat.phylogenetic_inference.tree.trie_postprocess import (
    AssignOriginTimeNodeRankTriePostprocessor,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def test_smoke():
    df = pl.read_csv(f"{assets_path}/packed.csv")
    raw = surface_unpack_reconstruct(df)
    res = surface_postprocess_trie(
        raw,
        trie_postprocessor=AssignOriginTimeNodeRankTriePostprocessor(
            t0="dstream_S",
        ),
    )
    assert "origin_time" in res.columns
    assert len(res) <= len(raw)
    assert alifestd_validate(
        alifestd_try_add_ancestor_list_col(res.to_pandas()),
    )
    assert alifestd_is_chronologically_ordered(res.to_pandas())


def test_hstrat_rank_retained():
    """hstrat_rank should be retained in output alongside hstrat_rank_from_t0."""
    df = pl.read_csv(f"{assets_path}/packed.csv")
    raw = surface_unpack_reconstruct(df)
    assert "hstrat_rank" in raw.columns
    res = surface_postprocess_trie(
        raw,
        trie_postprocessor=AssignOriginTimeNodeRankTriePostprocessor(
            t0="dstream_S",
        ),
    )
    assert "hstrat_rank" in res.columns
    assert "hstrat_rank_from_t0" in res.columns
