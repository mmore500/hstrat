import os
import typing

import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_mark_node_depth_asexual,
    alifestd_to_working_format,
)
from hstrat._auxiliary_lib._alifestd_mark_node_depth_polars import (
    alifestd_mark_node_depth_polars,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        alifestd_to_working_format(
            pd.read_csv(
                f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
            )
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv")
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_tournamentselection.csv")
        ),
    ],
)
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_fuzz_matches_pandas(
    phylogeny_df: pd.DataFrame, apply: typing.Callable
):
    """Verify polars node_depth matches pandas implementation on real data."""
    result_pd = alifestd_mark_node_depth_asexual(phylogeny_df, mutate=False)

    df_pl = apply(pl.from_pandas(phylogeny_df))
    result_pl = alifestd_mark_node_depth_polars(df_pl).lazy().collect()

    expected = result_pd["node_depth"].tolist()
    actual = result_pl["node_depth"].to_list()
    assert actual == expected


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_simple_chain(apply: typing.Callable):
    """Test a simple chain: 0 -> 1 -> 2."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 0, 1],
            }
        )
    )
    result = alifestd_mark_node_depth_polars(df_pl).lazy().collect()
    assert result["node_depth"].to_list() == [0, 1, 2]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_simple_tree(apply: typing.Callable):
    """Test: 0 (root) -> 1, 0 -> 2, 1 -> 3."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3],
                "ancestor_id": [0, 0, 0, 1],
            }
        )
    )
    result = alifestd_mark_node_depth_polars(df_pl).lazy().collect()
    assert result["node_depth"].to_list() == [0, 1, 1, 2]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_multiple_roots(apply: typing.Callable):
    """Each independent root should have depth 0."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 1, 2],
            }
        )
    )
    result = alifestd_mark_node_depth_polars(df_pl).lazy().collect()
    assert result["node_depth"].to_list() == [0, 0, 0]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_single_node(apply: typing.Callable):
    """A single root node should have depth 0."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0],
                "ancestor_id": [0],
            }
        )
    )
    result = alifestd_mark_node_depth_polars(df_pl).lazy().collect()
    assert result["node_depth"].to_list() == [0]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_empty(apply: typing.Callable):
    """Empty dataframe gets node_depth column."""
    df_pl = apply(
        pl.DataFrame(
            {"id": [], "ancestor_id": []},
            schema={"id": pl.Int64, "ancestor_id": pl.Int64},
        )
    )
    result = alifestd_mark_node_depth_polars(df_pl).lazy().collect()
    assert "node_depth" in result.columns
    assert result.is_empty()


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_preserves_columns(apply: typing.Callable):
    """Verify original columns are preserved and node_depth is added."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 0, 1],
                "origin_time": [0.0, 1.0, 2.0],
                "taxon_label": ["a", "b", "c"],
            }
        )
    )
    result = alifestd_mark_node_depth_polars(df_pl).lazy().collect()
    assert "node_depth" in result.columns
    assert "origin_time" in result.columns
    assert "taxon_label" in result.columns
    assert result["origin_time"].to_list() == [0.0, 1.0, 2.0]
    assert result["taxon_label"].to_list() == ["a", "b", "c"]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_with_ancestor_list_col(apply: typing.Callable):
    """Test that ancestor_list is correctly converted to ancestor_id."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3],
                "ancestor_list": ["[None]", "[0]", "[0]", "[1]"],
            }
        )
    )
    result = alifestd_mark_node_depth_polars(df_pl).lazy().collect()
    assert result["node_depth"].to_list() == [0, 1, 1, 2]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_does_not_mutate_input(apply: typing.Callable):
    """Verify the input dataframe is not mutated."""
    df_pl = pl.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 1, 0],
        }
    )
    original_data = df_pl.clone()

    alifestd_mark_node_depth_polars(apply(df_pl))

    assert df_pl.columns == original_data.columns
    assert df_pl.equals(original_data)
