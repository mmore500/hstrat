import os
import typing

import numpy as np
import pandas as pd
import polars as pl
import pytest
from tqdm import tqdm

from hstrat._auxiliary_lib import (
    alifestd_calc_mrca_id_matrix_asexual,
    alifestd_calc_mrca_id_vector_asexual,
    alifestd_is_chronologically_ordered,
    alifestd_to_working_format,
)
from hstrat._auxiliary_lib._alifestd_calc_mrca_id_vector_asexual_polars import (
    alifestd_calc_mrca_id_vector_asexual_polars,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def _make_actual_polars(
    phylogeny_df: pl.DataFrame,
    apply: typing.Callable,
) -> np.ndarray:
    """Build the full MRCA matrix by calling the polars vector function
    for every target_id, then stacking rows."""
    df_pl = apply(phylogeny_df)
    n = len(phylogeny_df)
    if n == 0:
        with pytest.raises(ValueError):
            alifestd_calc_mrca_id_vector_asexual_polars(df_pl, target_id=0)
        return np.zeros((0, 0), dtype=np.int64)
    res = [
        alifestd_calc_mrca_id_vector_asexual_polars(
            df_pl,
            target_id=i,
            progress_wrap=tqdm,
        )
        for i in range(n)
    ]
    return np.stack(res, axis=0)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
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
def test_big1_matches_pandas(
    phylogeny_df: pd.DataFrame, apply: typing.Callable
):
    """Verify polars result matches pandas MRCA matrix on real datasets."""
    phylogeny_df = phylogeny_df.copy()
    assert alifestd_is_chronologically_ordered(phylogeny_df)
    phylogeny_df = alifestd_to_working_format(phylogeny_df)
    df_pl = pl.from_pandas(phylogeny_df)

    expected = alifestd_calc_mrca_id_matrix_asexual(phylogeny_df)
    actual = _make_actual_polars(df_pl, apply)

    np.testing.assert_array_equal(expected, actual)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_simple1(apply: typing.Callable):
    """Test a simple 4-node tree matches known expected matrix."""
    phylogeny_df_pd = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_list": ["[None]", "[0]", "[1]", "[0]"],
        }
    )
    phylogeny_df_pd = alifestd_to_working_format(phylogeny_df_pd)
    df_pl = pl.from_pandas(phylogeny_df_pd)

    expected = np.array(
        [
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 2, 0],
            [0, 0, 0, 3],
        ],
        dtype=np.int64,
    )
    actual = _make_actual_polars(df_pl, apply)
    np.testing.assert_array_equal(actual, expected)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
@pytest.mark.parametrize(
    "phylogeny_df_pd",
    [
        pd.DataFrame(
            {
                "id": [],
                "ancestor_list": [],
            }
        ),
        pd.DataFrame(
            {
                "id": [],
                "ancestor_id": [],
            }
        ),
        pd.DataFrame(
            {
                "id": [0],
                "ancestor_list": ["[None]"],
            }
        ),
        pd.DataFrame(
            {
                "id": [0],
                "ancestor_id": [0],
                "ancestor_list": ["[None]"],
            }
        ),
        pd.DataFrame(
            {
                "id": [0, 1],
                "ancestor_list": ["[None]", "[0]"],
            }
        ),
        pd.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 1, 2],
            }
        ),
        pd.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 0, 0],
                "ancestor_list": ["[None]", "[0]", "[0]"],
            }
        ),
        pd.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_list": ["[None]", "[None]", "[1]"],
            }
        ),
        pd.DataFrame(
            {
                "id": [0, 1, 2, 3],
                "ancestor_id": [0, 0, 2, 1],
            }
        ),
        pd.DataFrame(
            {
                "id": [0, 1, 2, 3],
                "ancestor_id": [0, 0, 0, 0],
            }
        ),
        pd.DataFrame(
            {
                "id": [0, 1, 2, 3],
                "ancestor_list": ["[None]", "[0]", "[0]", "[0]"],
            }
        ),
    ],
)
def test_edge_cases(phylogeny_df_pd: pd.DataFrame, apply: typing.Callable):
    """Test edge cases match the pandas matrix implementation."""
    phylogeny_df_pd = phylogeny_df_pd.copy()

    expected = alifestd_calc_mrca_id_matrix_asexual(phylogeny_df_pd)

    # Prepare polars version — need working format for polars
    phylogeny_df_pd_wf = alifestd_to_working_format(phylogeny_df_pd.copy())
    df_pl = pl.from_pandas(phylogeny_df_pd_wf)

    actual = _make_actual_polars(df_pl, apply)
    np.testing.assert_array_equal(actual, expected)

    # idempotency check
    actual2 = _make_actual_polars(df_pl, apply)
    np.testing.assert_array_equal(actual2, expected)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_matches_pandas_vector(apply: typing.Callable):
    """Verify polars vector matches pandas vector for each target_id."""
    phylogeny_df_pd = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_list": ["[None]", "[0]", "[1]", "[0]"],
        }
    )
    phylogeny_df_pd = alifestd_to_working_format(phylogeny_df_pd)
    df_pl = pl.from_pandas(phylogeny_df_pd)

    for target_id in range(len(phylogeny_df_pd)):
        expected = alifestd_calc_mrca_id_vector_asexual(
            phylogeny_df_pd,
            mutate=False,
            target_id=target_id,
        )
        actual = alifestd_calc_mrca_id_vector_asexual_polars(
            apply(df_pl),
            target_id=target_id,
        )
        np.testing.assert_array_equal(actual, expected)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_target_id_out_of_bounds(apply: typing.Callable):
    """Verify ValueError raised for out-of-bounds target_id."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 0, 1],
            }
        )
    )
    with pytest.raises(ValueError):
        alifestd_calc_mrca_id_vector_asexual_polars(df_pl, target_id=3)

    with pytest.raises(ValueError):
        alifestd_calc_mrca_id_vector_asexual_polars(df_pl, target_id=100)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_empty_raises(apply: typing.Callable):
    """Verify ValueError raised for empty dataframe."""
    df_pl = apply(
        pl.DataFrame(
            {"id": [], "ancestor_id": []},
            schema={"id": pl.Int64, "ancestor_id": pl.Int64},
        )
    )
    with pytest.raises(ValueError):
        alifestd_calc_mrca_id_vector_asexual_polars(df_pl, target_id=0)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_single_node(apply: typing.Callable):
    """Test single-node phylogeny: MRCA with self is self."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0],
                "ancestor_id": [0],
            }
        )
    )
    result = alifestd_calc_mrca_id_vector_asexual_polars(df_pl, target_id=0)
    np.testing.assert_array_equal(result, np.array([0], dtype=np.int64))


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
    original_columns = df_pl.columns[:]
    original_data = df_pl.clone()

    alifestd_calc_mrca_id_vector_asexual_polars(apply(df_pl), target_id=1)

    assert df_pl.columns == original_columns
    assert df_pl.equals(original_data)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_multiple_roots(apply: typing.Callable):
    """Test phylogeny with multiple independent roots."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 1, 2],
            }
        )
    )
    # Each is its own root; MRCA of 0 with self is 0,
    # MRCA of 0 with 1 should be -1, MRCA of 0 with 2 should be -1
    result = alifestd_calc_mrca_id_vector_asexual_polars(df_pl, target_id=0)
    np.testing.assert_array_equal(
        result, np.array([0, -1, -1], dtype=np.int64)
    )


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_uint64_ancestor_id(apply: typing.Callable):
    """Regression: UInt64 ancestor_id caused numba float64 type unification."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": pl.Series([0, 1, 2, 3], dtype=pl.UInt64),
                "ancestor_id": pl.Series([0, 0, 1, 0], dtype=pl.UInt64),
            }
        )
    )
    result = alifestd_calc_mrca_id_vector_asexual_polars(df_pl, target_id=2)
    np.testing.assert_array_equal(
        result, np.array([0, 1, 2, 0], dtype=np.int64)
    )


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
    result = alifestd_calc_mrca_id_vector_asexual_polars(df_pl, target_id=2)
    # Tree: 0->1->3, 0->2.  MRCA(2,0)=0, MRCA(2,1)=0, MRCA(2,2)=2,
    # MRCA(2,3)=0
    np.testing.assert_array_equal(
        result, np.array([0, 0, 2, 0], dtype=np.int64)
    )
