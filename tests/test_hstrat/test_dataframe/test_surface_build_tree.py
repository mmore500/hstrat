import os
import re

import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_is_chronologically_ordered,
    alifestd_try_add_ancestor_list_col,
    alifestd_validate,
)
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
    assert alifestd_validate(
        alifestd_try_add_ancestor_list_col(res.to_pandas()),
    )
    assert alifestd_is_chronologically_ordered(res.to_pandas())


def test_drop_dstream_metadata_true_raises():
    """Passing drop_dstream_metadata=True should raise NotImplementedError."""
    df = pl.read_csv(f"{assets_path}/packed.csv")
    with pytest.raises(NotImplementedError):
        surface_build_tree(df, drop_dstream_metadata=True)


def test_drop_dstream_metadata_false():
    """Passing drop_dstream_metadata=False should retain dstream columns."""
    df = pl.read_csv(f"{assets_path}/packed.csv")
    res = surface_build_tree(
        df,
        collapse_unif_freq=0,
        drop_dstream_metadata=False,
        trie_postprocessor=AssignOriginTimeNodeRankTriePostprocessor(
            t0="dstream_S",
        ),
    )
    assert "origin_time" in res.columns
    assert len(df) <= len(res)
    # dstream columns from input should be forwarded, except for columns
    # consumed internally by surface_postprocess_trie
    postprocess_consumed = {"dstream_S", "hstrat_differentia_bitwidth"}
    input_dstream_cols = {
        c
        for c in df.columns
        if re.match(r"^dstream_", c) or re.match(r"^downstream_", c)
    } - postprocess_consumed
    output_dstream_cols = {
        c
        for c in res.columns
        if re.match(r"^dstream_", c) or re.match(r"^downstream_", c)
    }
    assert input_dstream_cols <= output_dstream_cols
