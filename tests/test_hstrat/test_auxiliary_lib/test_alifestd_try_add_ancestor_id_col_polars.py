import os

import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import alifestd_try_add_ancestor_id_col
from hstrat._auxiliary_lib._alifestd_try_add_ancestor_id_col_polars import (
    alifestd_try_add_ancestor_id_col as alifestd_try_add_ancestor_id_col_polars,
)

pytestmark = pytest.mark.filterwarnings(
    "ignore::polars.exceptions.PerformanceWarning"
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
def test_alifestd_try_add_ancestor_id_col_polars_asexual(phylogeny_df):
    """Verify ancestor_id column is correctly added for asexual phylogenies."""
    phylogeny_df_pl = pl.from_pandas(phylogeny_df).lazy()

    result = alifestd_try_add_ancestor_id_col_polars(phylogeny_df_pl)

    result_df = result.collect()
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
def test_alifestd_try_add_ancestor_id_col_polars_matches_pandas(
    phylogeny_df,
):
    """Verify polars result matches pandas result."""
    phylogeny_df_pd = phylogeny_df.copy()
    result_pd = alifestd_try_add_ancestor_id_col(phylogeny_df_pd)

    phylogeny_df_pl = pl.from_pandas(phylogeny_df).lazy()
    result_pl = alifestd_try_add_ancestor_id_col_polars(
        phylogeny_df_pl,
    ).collect()

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
def test_alifestd_try_add_ancestor_id_col_polars_sexual(phylogeny_df):
    """Verify ancestor_id is NOT added for sexual phylogenies."""
    phylogeny_df_pl = pl.from_pandas(phylogeny_df).lazy()

    result = alifestd_try_add_ancestor_id_col_polars(phylogeny_df_pl)

    result_df = result.collect()
    assert "ancestor_id" not in result_df.columns


def test_alifestd_try_add_ancestor_id_col_polars_already_has_ancestor_id():
    """Verify no change when ancestor_id column already exists."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[none]", "[0]", "[1]"],
            "ancestor_id": [0, 0, 1],
        }
    ).lazy()

    result = alifestd_try_add_ancestor_id_col_polars(df)

    result_df = result.collect()
    assert result_df["ancestor_id"].to_list() == [0, 0, 1]


def test_alifestd_try_add_ancestor_id_col_polars_simple_chain():
    """Test a simple chain: 0 -> 1 -> 2."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[none]", "[0]", "[1]"],
        }
    ).lazy()

    result = alifestd_try_add_ancestor_id_col_polars(df)

    result_df = result.collect()
    assert "ancestor_id" in result_df.columns
    assert result_df["ancestor_id"].to_list() == [0, 0, 1]


def test_alifestd_try_add_ancestor_id_col_polars_simple_tree():
    """Test a simple tree.

    Tree structure:
        0 (root)
        ├── 1
        │   ├── 3
        │   └── 4
        └── 2
    """
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[none]", "[0]", "[0]", "[1]", "[1]"],
        }
    ).lazy()

    result = alifestd_try_add_ancestor_id_col_polars(df)

    result_df = result.collect()
    assert result_df["ancestor_id"].to_list() == [0, 0, 0, 1, 1]


def test_alifestd_try_add_ancestor_id_col_polars_single_node():
    """A single root node."""
    df = pl.DataFrame(
        {
            "id": [0],
            "ancestor_list": ["[none]"],
        }
    ).lazy()

    result = alifestd_try_add_ancestor_id_col_polars(df)

    result_df = result.collect()
    assert "ancestor_id" in result_df.columns
    # Root node should have ancestor_id == id
    assert result_df["ancestor_id"].to_list() == [0]


def test_alifestd_try_add_ancestor_id_col_polars_two_roots():
    """Two independent root nodes."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_list": ["[none]", "[none]", "[0]", "[1]"],
        }
    ).lazy()

    result = alifestd_try_add_ancestor_id_col_polars(df)

    result_df = result.collect()
    assert "ancestor_id" in result_df.columns
    assert result_df["ancestor_id"].to_list() == [0, 1, 0, 1]


def test_alifestd_try_add_ancestor_id_col_polars_empty():
    """Verify empty dataframe gets ancestor_id column."""
    df = pl.DataFrame(
        {"id": [], "ancestor_list": []},
        schema={"id": pl.Int64, "ancestor_list": pl.String},
    ).lazy()

    result = alifestd_try_add_ancestor_id_col_polars(df)

    result_df = result.collect()
    assert "ancestor_id" in result_df.columns
    assert result_df.is_empty()


def test_alifestd_try_add_ancestor_id_col_polars_preserves_columns():
    """Verify original columns are preserved."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[none]", "[0]", "[1]"],
            "origin_time": [0.0, 1.0, 2.0],
            "taxon_label": ["a", "b", "c"],
        }
    ).lazy()

    result = alifestd_try_add_ancestor_id_col_polars(df)

    result_df = result.collect()
    assert "ancestor_id" in result_df.columns
    assert "origin_time" in result_df.columns
    assert "taxon_label" in result_df.columns
    assert result_df["origin_time"].to_list() == [0.0, 1.0, 2.0]
    assert result_df["taxon_label"].to_list() == ["a", "b", "c"]


def test_alifestd_try_add_ancestor_id_col_polars_idempotent():
    """Calling twice should produce the same result."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[none]", "[0]", "[1]"],
        }
    ).lazy()

    result1 = alifestd_try_add_ancestor_id_col_polars(df).collect()
    result2 = alifestd_try_add_ancestor_id_col_polars(
        result1.lazy(),
    ).collect()

    assert result1["ancestor_id"].to_list() == result2["ancestor_id"].to_list()
