import typing

import pandas as pd
import polars as pl
import pytest

from hstrat import hstrat
from hstrat._auxiliary_lib import coerce_to_pandas
import hstrat.phylogenetic_inference.tree.trie_postprocess._detail as detail


def test_base_class():
    assert issubclass(
        hstrat.NopTriePostprocessor,
        detail.TriePostprocessorBase,
    )


@pytest.mark.parametrize("df_type", [pd.DataFrame, pl.DataFrame])
def test_nop_mutate(df_type: typing.Type):
    df = df_type(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 1, 2],
            "rank": [0, 0, 0, 0],
            "taxon_label": [None, None, "A", "B"],
            "differentia": [None, 0, None, None],
        },
    )
    df_ = hstrat.NopTriePostprocessor()(
        df, p_differentia_collision=0.5, mutate=False
    )
    assert df is not df_
    pd.testing.assert_frame_equal(coerce_to_pandas(df), coerce_to_pandas(df_))

    df = hstrat.NopTriePostprocessor()(
        df, p_differentia_collision=0.5, mutate=True
    )
    pd.testing.assert_frame_equal(coerce_to_pandas(df), coerce_to_pandas(df_))
