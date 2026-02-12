import os
import typing

import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import alifestd_has_contiguous_ids
from hstrat._auxiliary_lib._alifestd_has_contiguous_ids_polars import (
    alifestd_has_contiguous_ids_polars,
)

pytestmark = pytest.mark.filterwarnings(
    "ignore::polars.exceptions.PerformanceWarning"
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-sexual-phylogeny.csv"
        ),
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        )[0:1],
    ],
)
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_has_contiguous_ids_polars_true(
    phylogeny_df: pd.DataFrame, apply: typing.Callable
):
    """Verify returns True for datasets with contiguous ids."""
    df = apply(pl.from_pandas(phylogeny_df))
    assert alifestd_has_contiguous_ids_polars(df)


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
def test_alifestd_has_contiguous_ids_polars_false(
    phylogeny_df: pd.DataFrame, apply: typing.Callable
):
    """Verify returns False for datasets with non-contiguous ids."""
    df = apply(pl.from_pandas(phylogeny_df))
    assert not alifestd_has_contiguous_ids_polars(df)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-sexual-phylogeny.csv"
        ),
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
def test_alifestd_has_contiguous_ids_polars_matches_pandas(
    phylogeny_df: pd.DataFrame, apply: typing.Callable
):
    """Verify polars result matches pandas result."""
    result_pd = alifestd_has_contiguous_ids(phylogeny_df)
    df = apply(pl.from_pandas(phylogeny_df))
    result_pl = alifestd_has_contiguous_ids_polars(df)
    assert result_pd == result_pl


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_has_contiguous_ids_polars_simple_true(
    apply: typing.Callable,
):
    """Ids 0, 1, 2 are contiguous."""
    df = apply(pl.DataFrame({"id": [0, 1, 2]}))
    assert alifestd_has_contiguous_ids_polars(df)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_has_contiguous_ids_polars_simple_false_gap(
    apply: typing.Callable,
):
    """Ids 0, 2, 4 have gaps."""
    df = apply(pl.DataFrame({"id": [0, 2, 4]}))
    assert not alifestd_has_contiguous_ids_polars(df)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_has_contiguous_ids_polars_simple_false_start(
    apply: typing.Callable,
):
    """Ids starting at 1 are not contiguous (must start at 0)."""
    df = apply(pl.DataFrame({"id": [1, 2, 3]}))
    assert not alifestd_has_contiguous_ids_polars(df)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_has_contiguous_ids_polars_single_node(
    apply: typing.Callable,
):
    """Single node with id 0."""
    df = apply(pl.DataFrame({"id": [0]}))
    assert alifestd_has_contiguous_ids_polars(df)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_has_contiguous_ids_polars_single_node_nonzero(
    apply: typing.Callable,
):
    """Single node with id != 0."""
    df = apply(pl.DataFrame({"id": [5]}))
    assert not alifestd_has_contiguous_ids_polars(df)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_has_contiguous_ids_polars_empty(apply: typing.Callable):
    """Empty dataframe."""
    df = apply(pl.DataFrame({"id": []}, schema={"id": pl.Int64}))
    assert alifestd_has_contiguous_ids_polars(df)
