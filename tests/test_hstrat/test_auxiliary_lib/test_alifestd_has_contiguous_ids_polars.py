import os

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


@pytest.fixture(
    params=[
        pytest.param(False, id="DataFrame"),
        pytest.param(True, id="LazyFrame"),
    ]
)
def lazy(request):
    return request.param


def _apply_lazy(df: pl.DataFrame, lazy: bool):
    """Return DataFrame or LazyFrame depending on fixture."""
    if lazy:
        return df.lazy()
    return df


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
def test_alifestd_has_contiguous_ids_polars_true(phylogeny_df, lazy):
    """Verify returns True for datasets with contiguous ids."""
    df = _apply_lazy(pl.from_pandas(phylogeny_df), lazy)
    assert alifestd_has_contiguous_ids_polars(df)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_alifestd_has_contiguous_ids_polars_false(phylogeny_df, lazy):
    """Verify returns False for datasets with non-contiguous ids."""
    df = _apply_lazy(pl.from_pandas(phylogeny_df), lazy)
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
def test_alifestd_has_contiguous_ids_polars_matches_pandas(
    phylogeny_df, lazy
):
    """Verify polars result matches pandas result."""
    result_pd = alifestd_has_contiguous_ids(phylogeny_df)
    df = _apply_lazy(pl.from_pandas(phylogeny_df), lazy)
    result_pl = alifestd_has_contiguous_ids_polars(df)
    assert result_pd == result_pl


def test_alifestd_has_contiguous_ids_polars_simple_true(lazy):
    """Ids 0, 1, 2 are contiguous."""
    df = _apply_lazy(pl.DataFrame({"id": [0, 1, 2]}), lazy)
    assert alifestd_has_contiguous_ids_polars(df)


def test_alifestd_has_contiguous_ids_polars_simple_false_gap(lazy):
    """Ids 0, 2, 4 have gaps."""
    df = _apply_lazy(pl.DataFrame({"id": [0, 2, 4]}), lazy)
    assert not alifestd_has_contiguous_ids_polars(df)


def test_alifestd_has_contiguous_ids_polars_simple_false_start(lazy):
    """Ids starting at 1 are not contiguous (must start at 0)."""
    df = _apply_lazy(pl.DataFrame({"id": [1, 2, 3]}), lazy)
    assert not alifestd_has_contiguous_ids_polars(df)


def test_alifestd_has_contiguous_ids_polars_single_node(lazy):
    """Single node with id 0."""
    df = _apply_lazy(pl.DataFrame({"id": [0]}), lazy)
    assert alifestd_has_contiguous_ids_polars(df)


def test_alifestd_has_contiguous_ids_polars_single_node_nonzero(lazy):
    """Single node with id != 0."""
    df = _apply_lazy(pl.DataFrame({"id": [5]}), lazy)
    assert not alifestd_has_contiguous_ids_polars(df)


def test_alifestd_has_contiguous_ids_polars_empty(lazy):
    """Empty dataframe."""
    df = _apply_lazy(
        pl.DataFrame({"id": []}, schema={"id": pl.Int64}), lazy
    )
    assert alifestd_has_contiguous_ids_polars(df)
