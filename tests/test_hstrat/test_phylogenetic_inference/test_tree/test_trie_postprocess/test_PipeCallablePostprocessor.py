import os

import polars as pl
import pytest

from hstrat import hstrat
from hstrat.dataframe import surface_build_tree

assets = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "../../../test_dataframe/assets",
)


def test_pipe():
    trie = pl.DataFrame({"id": [0, 1], "ancestor_id": [0, 0]})
    result = hstrat.PipeCallablePostprocessor(
        lambda df: df.with_columns(foo=pl.lit("bar")),
    )(trie, p_differentia_collision=0.5)
    assert result["foo"].to_list() == ["bar", "bar"]
    assert "foo" not in trie.columns


def test_pipe_args_kwargs():
    def add_column(df: pl.DataFrame, name: str, *, value: int):
        return df.with_columns(pl.lit(value).alias(name))

    trie = pl.DataFrame({"id": [0], "ancestor_id": [0]})
    result = hstrat.PipeCallablePostprocessor(add_column, "foo", value=7)(
        trie, p_differentia_collision=0.5, mutate=True
    )
    assert result["foo"].to_list() == [7]


def test_polars_only():
    trie = pl.DataFrame({"id": [0], "ancestor_id": [0]})
    with pytest.raises(NotImplementedError):
        hstrat.PipeCallablePostprocessor(lambda df: df)(
            trie.to_pandas(), p_differentia_collision=0.5
        )


def test_surface_build_tree():
    df = pl.read_csv(f"{assets}/packed.csv")
    phylo = surface_build_tree(
        df,
        trie_postprocessor=hstrat.PipeCallablePostprocessor(
            lambda trie: trie.with_columns(foo=pl.lit("bar")),
        ),
    )
    assert (phylo["foo"] == "bar").all()
