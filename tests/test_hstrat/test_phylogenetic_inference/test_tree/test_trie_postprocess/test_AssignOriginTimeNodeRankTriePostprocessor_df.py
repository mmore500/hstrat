import typing

import pandas as pd
import polars as pl
import pytest

from hstrat import hstrat
from hstrat._auxiliary_lib import coerce_to_pandas
import hstrat.phylogenetic_inference.tree.trie_postprocess._detail as detail


def test_base_class():
    assert issubclass(
        hstrat.AssignOriginTimeNodeRankTriePostprocessor,
        detail.TriePostprocessorBase,
    )


@pytest.mark.parametrize("df_type", [pd.DataFrame, pl.DataFrame])
def test_assign_trie_origin_times_node_rank_single_leaf(df_type: typing.Type):
    df = df_type(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 1],
            "rank": [0, 0, 0],
            "taxon_label": [None, None, "A"],
            "differentia": [None, 0, None],
        },
    )
    df = hstrat.AssignOriginTimeNodeRankTriePostprocessor()(
        df, p_differentia_collision=0.5, mutate=True
    )
    df = coerce_to_pandas(df)
    assert df.loc[0, "origin_time"] == 0
    assert df.loc[1, "origin_time"] == 0
    assert df.loc[2, "origin_time"] == 0


@pytest.mark.parametrize("df_type", [pd.DataFrame, pl.DataFrame])
def test_assign_trie_origin_times_node_rank_two_leaves(df_type: typing.Type):
    df = df_type(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 1, 2],
            "rank": [0, 0, 0, 0],
            "taxon_label": [None, None, "A", "B"],
            "differentia": [None, 0, None, None],
            "t0_": [1, 1, 1, 1],
        },
    )
    df = hstrat.AssignOriginTimeNodeRankTriePostprocessor(t0="t0_")(
        df, p_differentia_collision=0.5, mutate=True
    )
    df = coerce_to_pandas(df)
    assert df.loc[0, "origin_time"] == 0 - 1
    assert df.loc[1, "origin_time"] == 0 - 1
    assert df.loc[2, "origin_time"] == 0 - 1
    assert df.loc[3, "origin_time"] == 0 - 1


@pytest.mark.parametrize("df_type", [pd.DataFrame, pl.DataFrame])
def test_assign_trie_origin_times_node_rank1(df_type: typing.Type):
    df = df_type(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 1, 2],
            "rank": [0, 0, 1, 1],
            "taxon_label": [None, None, "A", "B"],
            "differentia": [None, 0, None, None],
        },
    )
    df = hstrat.AssignOriginTimeNodeRankTriePostprocessor()(
        df, p_differentia_collision=0.5, mutate=True
    )
    df = coerce_to_pandas(df)
    assert df.loc[0, "origin_time"] == 0
    assert df.loc[1, "origin_time"] == 0
    assert df.loc[2, "origin_time"] == 1
    assert df.loc[3, "origin_time"] == 1


@pytest.mark.parametrize("df_type", [pd.DataFrame, pl.DataFrame])
def test_assign_trie_origin_times_node_rank2(df_type: typing.Type):
    df = df_type(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 1, 2],
            "rank": [0, 0, 2, 2],
            "taxon_label": [None, None, "A", "B"],
            "differentia": [None, 0, None, None],
        },
    )
    df = hstrat.AssignOriginTimeNodeRankTriePostprocessor()(
        df, p_differentia_collision=0.5, mutate=True
    )
    df = coerce_to_pandas(df)
    assert df.loc[0, "origin_time"] == 0
    assert df.loc[1, "origin_time"] == 0
    assert df.loc[2, "origin_time"] == 2
    assert df.loc[3, "origin_time"] == 2


@pytest.mark.parametrize("df_type", [pd.DataFrame, pl.DataFrame])
def test_assign_trie_origin_times_node_rank3(df_type: typing.Type):
    df = df_type(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 1, 2],
            "rank": [0, 0, 3, 3],
            "taxon_label": [None, None, "A", "B"],
            "differentia": [None, 0, 10, None],
        },
    )
    df = hstrat.AssignOriginTimeNodeRankTriePostprocessor()(
        df, p_differentia_collision=0.5, mutate=True
    )
    df = coerce_to_pandas(df)
    assert df.loc[0, "origin_time"] == 0
    assert df.loc[1, "origin_time"] == 0
    assert df.loc[2, "origin_time"] == 3
    assert df.loc[3, "origin_time"] == 3


@pytest.mark.parametrize("df_type", [pd.DataFrame, pl.DataFrame])
def test_assign_trie_origin_times_node_rank_complex(df_type: typing.Type):
    df = df_type(
        {
            "id": [0, 1, 2, 3, 4, 5, 6, 7],
            "ancestor_id": [0, 0, 1, 2, 1, 2, 3, 3],
            "rank": [0, 0, 4, 7, 4, 7, 10, 10],
            "taxon_label": [None, None, "A", "B", "C", "D", "E", "F"],
            "differentia": [None, 0, 10, 7, 1, None, None, None],
        },
    )
    df = hstrat.AssignOriginTimeNodeRankTriePostprocessor(t0=-1)(
        df, p_differentia_collision=0.5, mutate=True
    )
    df = coerce_to_pandas(df)
    assert df.loc[0, "origin_time"] == 0 + 1
    assert df.loc[1, "origin_time"] == 0 + 1
    assert df.loc[2, "origin_time"] == 4 + 1
    assert df.loc[3, "origin_time"] == 7 + 1
    assert df.loc[4, "origin_time"] == 4 + 1
    assert df.loc[5, "origin_time"] == 7 + 1
    assert df.loc[6, "origin_time"] == 10 + 1
    assert df.loc[7, "origin_time"] == 10 + 1


@pytest.mark.parametrize("df_type", [pd.DataFrame, pl.DataFrame])
def test_assign_trie_origin_times_node_rank_assigned_property(
    df_type: typing.Type,
):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 1, 2],
            "rank": [0, 0, 0, 0],
            "taxon_label": [None, None, "A", "B"],
            "differentia": [None, 0, None, None],
        },
    )
    df = hstrat.AssignOriginTimeNodeRankTriePostprocessor(
        assigned_property="blueberry",
    )(df, p_differentia_collision=0.5, mutate=True)
    assert df.loc[0, "blueberry"] == 0
    assert df.loc[1, "blueberry"] == 0
    assert df.loc[2, "blueberry"] == 0


@pytest.mark.parametrize("df_type", [pd.DataFrame, pl.DataFrame])
def test_assign_trie_origin_times_node_rank_mutate(df_type: typing.Type):
    df = df_type(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 1, 2],
            "rank": [0, 0, 0, 0],
            "taxon_label": [None, None, "A", "B"],
            "differentia": [None, 0, None, None],
        },
    )
    df_ = hstrat.AssignOriginTimeNodeRankTriePostprocessor()(
        df, p_differentia_collision=0.5, mutate=False
    )
    assert "origin_time" in df_.columns
    assert "origin_time" not in df.columns
    df = hstrat.AssignOriginTimeNodeRankTriePostprocessor(
        assigned_property="blueberry",
    )(df, p_differentia_collision=0.5, mutate=True)
    assert "blueberry" in df.columns
