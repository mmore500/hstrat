import os
import typing

import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_try_add_ancestor_id_col,
    alifestd_try_add_ancestor_id_col_polars,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_try_add_ancestor_id_col_polars_asexual(
    phylogeny_df, apply: typing.Callable
):
    """Verify ancestor_id column is correctly added for asexual phylogenies."""
    df_prepared = pl.from_pandas(phylogeny_df)
    df = apply(df_prepared)

    result_df = alifestd_try_add_ancestor_id_col_polars(df).lazy().collect()

    assert "ancestor_id" in result_df.columns
    assert len(result_df) == len(phylogeny_df)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_try_add_ancestor_id_col_polars_matches_pandas(
    phylogeny_df, apply: typing.Callable
):
    """Verify polars result matches pandas result."""
    result_pd = alifestd_try_add_ancestor_id_col(phylogeny_df.copy())

    df = apply(pl.from_pandas(phylogeny_df))
    result_pl = alifestd_try_add_ancestor_id_col_polars(df).lazy().collect()

    assert "ancestor_id" in result_pd.columns
    assert "ancestor_id" in result_pl.columns

    pd_ids = result_pd["ancestor_id"].tolist()
    pl_ids = result_pl["ancestor_id"].to_list()
    assert pd_ids == pl_ids


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-sexual-phylogeny.csv"
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
def test_alifestd_try_add_ancestor_id_col_polars_sexual(
    phylogeny_df, apply: typing.Callable
):
    """Verify ancestor_id is NOT added for sexual phylogenies."""
    df = apply(pl.from_pandas(phylogeny_df))

    result_df = alifestd_try_add_ancestor_id_col_polars(df).lazy().collect()

    assert "ancestor_id" not in result_df.columns


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_try_add_ancestor_id_col_polars_already_has_ancestor_id(
    apply: typing.Callable,
):
    """Verify no change when ancestor_id column already exists."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_list": ["[none]", "[0]", "[1]"],
                "ancestor_id": [0, 0, 1],
            }
        )
    )

    result_df = alifestd_try_add_ancestor_id_col_polars(df).lazy().collect()

    assert result_df["ancestor_id"].to_list() == [0, 0, 1]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_try_add_ancestor_id_col_polars_simple_chain(
    apply: typing.Callable,
):
    """Test a simple chain: 0 -> 1 -> 2."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_list": ["[]", "[0]", "[1]"],
            }
        )
    )

    result_df = alifestd_try_add_ancestor_id_col_polars(df).lazy().collect()

    assert "ancestor_id" in result_df.columns
    assert result_df["ancestor_id"].to_list() == [0, 0, 1]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_try_add_ancestor_id_col_polars_simple_tree(
    apply: typing.Callable,
):
    """Test a simple tree.

    Tree structure:
        0 (root)
        +-- 1
        |   +-- 3
        |   +-- 4
        +-- 2
    """
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3, 4],
                "ancestor_list": ["[None]", "[0]", "[0]", "[1]", "[1]"],
            }
        )
    )

    result_df = alifestd_try_add_ancestor_id_col_polars(df).lazy().collect()

    assert result_df["ancestor_id"].to_list() == [0, 0, 0, 1, 1]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_try_add_ancestor_id_col_polars_single_node(
    apply: typing.Callable,
):
    """A single root node."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0],
                "ancestor_list": ["[none]"],
            }
        )
    )

    result_df = alifestd_try_add_ancestor_id_col_polars(df).lazy().collect()

    assert "ancestor_id" in result_df.columns
    assert result_df["ancestor_id"].to_list() == [0]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_try_add_ancestor_id_col_polars_two_roots(
    apply: typing.Callable,
):
    """Two independent root nodes."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3],
                "ancestor_list": ["[none]", "[none]", "[0]", "[1]"],
            }
        )
    )

    result_df = alifestd_try_add_ancestor_id_col_polars(df).lazy().collect()

    assert "ancestor_id" in result_df.columns
    assert result_df["ancestor_id"].to_list() == [0, 1, 0, 1]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_try_add_ancestor_id_col_polars_empty(
    apply: typing.Callable,
):
    """Verify empty dataframe gets ancestor_id column."""
    df = apply(
        pl.DataFrame(
            {"id": [], "ancestor_list": []},
            schema={"id": pl.Int64, "ancestor_list": pl.String},
        )
    )

    result_df = alifestd_try_add_ancestor_id_col_polars(df).lazy().collect()

    assert "ancestor_id" in result_df.columns
    assert result_df.is_empty()


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_try_add_ancestor_id_col_polars_preserves_columns(
    apply: typing.Callable,
):
    """Verify original columns are preserved."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_list": ["[none]", "[0]", "[1]"],
                "origin_time": [0.0, 1.0, 2.0],
                "taxon_label": ["a", "b", "c"],
            }
        )
    )

    result_df = alifestd_try_add_ancestor_id_col_polars(df).lazy().collect()

    assert "ancestor_id" in result_df.columns
    assert "origin_time" in result_df.columns
    assert "taxon_label" in result_df.columns
    assert result_df["origin_time"].to_list() == [0.0, 1.0, 2.0]
    assert result_df["taxon_label"].to_list() == ["a", "b", "c"]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_try_add_ancestor_id_col_polars_idempotent(
    apply: typing.Callable,
):
    """Calling twice should produce the same result."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_list": ["[none]", "[0]", "[1]"],
            }
        )
    )

    result1 = alifestd_try_add_ancestor_id_col_polars(df).lazy().collect()
    result2 = (
        alifestd_try_add_ancestor_id_col_polars(apply(result1))
        .lazy()
        .collect()
    )

    assert result1["ancestor_id"].to_list() == result2["ancestor_id"].to_list()
