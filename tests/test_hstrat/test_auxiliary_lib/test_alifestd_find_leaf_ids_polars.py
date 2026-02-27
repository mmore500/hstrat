import os
import typing

import numpy as np
import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_find_leaf_ids,
    alifestd_to_working_format,
)
from hstrat._auxiliary_lib._alifestd_find_leaf_ids_polars import (
    alifestd_find_leaf_ids_polars,
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
def test_alifestd_find_leaf_ids_polars_matches_pandas(
    phylogeny_df: pd.DataFrame, apply: typing.Callable
):
    """Verify polars result matches pandas result on real data."""
    expected = alifestd_find_leaf_ids(phylogeny_df)

    df_pl = apply(pl.from_pandas(phylogeny_df))
    actual = alifestd_find_leaf_ids_polars(df_pl)

    assert isinstance(actual, np.ndarray)
    np.testing.assert_array_equal(sorted(actual), sorted(expected))


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_find_leaf_ids_polars_empty(apply: typing.Callable):
    """Empty dataframe returns empty array."""
    df_pl = apply(
        pl.DataFrame(
            {"id": [], "ancestor_id": []},
            schema={"id": pl.Int64, "ancestor_id": pl.Int64},
        ),
    )

    result = alifestd_find_leaf_ids_polars(df_pl)

    assert isinstance(result, np.ndarray)
    assert len(result) == 0


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_find_leaf_ids_polars_singleton(apply: typing.Callable):
    """A single root node with no children is a leaf."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0],
                "ancestor_id": [0],
            }
        ),
    )

    result = alifestd_find_leaf_ids_polars(df_pl)

    assert isinstance(result, np.ndarray)
    assert result.tolist() == [0]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_find_leaf_ids_polars_simple_chain(apply: typing.Callable):
    """Test a simple chain: 0 -> 1 -> 2. Only node 2 is a leaf."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 0, 1],
            }
        ),
    )

    result = alifestd_find_leaf_ids_polars(df_pl)

    assert isinstance(result, np.ndarray)
    assert result.tolist() == [2]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_find_leaf_ids_polars_simple_tree(apply: typing.Callable):
    """Test a simple tree.

    Tree structure:
        0 (root)
        +-- 1
        |   +-- 3 (leaf)
        |   +-- 4 (leaf)
        +-- 2 (leaf)
    """
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3, 4],
                "ancestor_id": [0, 0, 0, 1, 1],
            }
        ),
    )

    result = alifestd_find_leaf_ids_polars(df_pl)

    assert isinstance(result, np.ndarray)
    assert sorted(result.tolist()) == [2, 3, 4]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_find_leaf_ids_polars_two_roots(apply: typing.Callable):
    """Two independent roots with children."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3],
                "ancestor_id": [0, 1, 0, 1],
            }
        ),
    )

    result = alifestd_find_leaf_ids_polars(df_pl)

    assert isinstance(result, np.ndarray)
    assert sorted(result.tolist()) == [2, 3]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_find_leaf_ids_polars_all_leaves(apply: typing.Callable):
    """Multiple roots (all self-referencing) are all leaves."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 1, 2],
            }
        ),
    )

    result = alifestd_find_leaf_ids_polars(df_pl)

    assert isinstance(result, np.ndarray)
    assert sorted(result.tolist()) == [0, 1, 2]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_find_leaf_ids_polars_polytomy(apply: typing.Callable):
    """Test polytomy: root with many children."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3, 4],
                "ancestor_id": [0, 0, 0, 0, 1],
            }
        ),
    )

    result = alifestd_find_leaf_ids_polars(df_pl)

    assert isinstance(result, np.ndarray)
    assert sorted(result.tolist()) == [2, 3, 4]
