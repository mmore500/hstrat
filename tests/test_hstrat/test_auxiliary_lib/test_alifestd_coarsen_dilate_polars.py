import typing

import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib._alifestd_coarsen_dilate_asexual import (
    alifestd_coarsen_dilate_asexual,
)
from hstrat._auxiliary_lib._alifestd_coarsen_dilate_polars import (
    alifestd_coarsen_dilate_polars,
)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_empty(apply: typing.Callable):
    df = pl.DataFrame(
        {
            "id": pl.Series([], dtype=pl.Int64),
            "ancestor_id": pl.Series([], dtype=pl.Int64),
            "origin_time": pl.Series([], dtype=pl.Float64),
        }
    )
    result = alifestd_coarsen_dilate_polars(
        apply(df),
        dilation=2,
        ignore_topological_sensitivity=True,
    )
    assert len(result) == 0


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_singleton(apply: typing.Callable):
    df = pl.DataFrame(
        {
            "id": [0],
            "ancestor_id": [0],
            "origin_time": [5],
        }
    )
    result = alifestd_coarsen_dilate_polars(
        apply(df),
        dilation=2,
        ignore_topological_sensitivity=True,
    )
    assert len(result) == 1
    assert result["id"][0] == 0
    assert result["origin_time"][0] == 5  # leaf, unchanged


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_chain_dilation2(apply: typing.Callable):
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 1, 2, 3],
            "origin_time": [0, 1, 2, 3, 4],
        }
    )
    result = alifestd_coarsen_dilate_polars(
        apply(df),
        dilation=2,
        ignore_topological_sensitivity=True,
    )
    result_ids = sorted(result["id"].to_list())
    assert result_ids == [0, 2, 4]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_branching_tree(apply: typing.Callable):
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_id": [0, 0, 0, 1, 2, 3, 4],
            "origin_time": [0, 1, 1, 2, 3, 4, 5],
        }
    )
    result = alifestd_coarsen_dilate_polars(
        apply(df),
        dilation=2,
        ignore_topological_sensitivity=True,
    )
    result_ids = sorted(result["id"].to_list())
    assert result_ids == [0, 3, 4, 5, 6]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_float_criterion(apply: typing.Callable):
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 1, 2, 3],
            "origin_time": [0.0, 1.5, 3.0, 4.5, 6.0],
        }
    )
    result = alifestd_coarsen_dilate_polars(
        apply(df),
        dilation=3,
        ignore_topological_sensitivity=True,
    )
    result_ids = sorted(result["id"].to_list())
    assert result_ids == [0, 2, 4]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_matches_pandas(apply: typing.Callable):
    """Verify polars result matches pandas result."""
    df_pd = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_id": [0, 0, 0, 1, 2, 3, 4],
            "origin_time": [0, 1, 1, 2, 3, 4, 5],
        }
    )
    df_pl = pl.from_pandas(df_pd)

    result_pd = alifestd_coarsen_dilate_asexual(
        df_pd,
        dilation=2,
        ignore_topological_sensitivity=True,
    )
    result_pl = alifestd_coarsen_dilate_polars(
        apply(df_pl),
        dilation=2,
        ignore_topological_sensitivity=True,
    )

    pd.testing.assert_frame_equal(
        result_pd.sort_values("id").reset_index(drop=True),
        result_pl.to_pandas().sort_values("id").reset_index(drop=True),
        check_dtype=False,
    )


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_matches_pandas_large_dilation(apply: typing.Callable):
    df_pd = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 1, 2, 3],
            "origin_time": [0, 1, 2, 3, 4],
        }
    )
    df_pl = pl.from_pandas(df_pd)

    result_pd = alifestd_coarsen_dilate_asexual(
        df_pd,
        dilation=100,
        ignore_topological_sensitivity=True,
    )
    result_pl = alifestd_coarsen_dilate_polars(
        apply(df_pl),
        dilation=100,
        ignore_topological_sensitivity=True,
    )

    pd.testing.assert_frame_equal(
        result_pd.sort_values("id").reset_index(drop=True),
        result_pl.to_pandas().sort_values("id").reset_index(drop=True),
        check_dtype=False,
    )


def test_invalid_dilation():
    df = pl.DataFrame(
        {
            "id": [0],
            "ancestor_id": [0],
            "origin_time": [0],
        }
    )
    with pytest.raises(ValueError, match="dilation must be positive"):
        alifestd_coarsen_dilate_polars(
            df,
            dilation=0,
            ignore_topological_sensitivity=True,
        )


def test_missing_criterion():
    df = pl.DataFrame(
        {
            "id": [0],
            "ancestor_id": [0],
        }
    )
    with pytest.raises(ValueError, match="criterion column"):
        alifestd_coarsen_dilate_polars(
            df,
            dilation=2,
            ignore_topological_sensitivity=True,
        )


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_leaves_preserved(apply: typing.Callable):
    """All leaf nodes must appear in the result."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_id": [0, 0, 0, 1, 2, 3, 4],
            "origin_time": [0, 1, 1, 2, 3, 4, 5],
        }
    )
    # Leaf ids: 5, 6 (never appear as ancestor of another)
    # Also 3 isn't ancestor to anything? Let's verify:
    # ancestors used: 0,0,0,1,2,3,4 -> {0,1,2,3,4}
    # So leaves are: 5, 6
    result = alifestd_coarsen_dilate_polars(
        apply(df),
        dilation=2,
        ignore_topological_sensitivity=True,
    )
    result_ids = set(result["id"].to_list())
    assert 5 in result_ids
    assert 6 in result_ids


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_custom_criterion(apply: typing.Callable):
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 1, 2, 3],
            "origin_time": [10, 20, 30, 40, 50],
            "my_time": [0, 1, 2, 3, 4],
        }
    )
    result = alifestd_coarsen_dilate_polars(
        apply(df),
        dilation=2,
        criterion="my_time",
        ignore_topological_sensitivity=True,
    )
    result_ids = sorted(result["id"].to_list())
    assert result_ids == [0, 2, 4]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_no_topological_change_still_snaps(apply: typing.Callable):
    df = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 1],
            "origin_time": [0, 5, 10],
        }
    )
    result = alifestd_coarsen_dilate_polars(
        apply(df),
        dilation=3,
        ignore_topological_sensitivity=True,
    )
    assert len(result) == 3
    ot = dict(zip(result["id"].to_list(), result["origin_time"].to_list()))
    assert ot[0] == 0
    assert ot[1] == 3  # snapped from 5 to 3
    assert ot[2] == 10  # leaf unchanged
