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
        pytest.param(False, id="direct"),
        pytest.param(True, id="lazy-roundtrip"),
    ]
)
def lazy_roundtrip(request):
    return request.param


def _to_lazyframe(df: pl.DataFrame, lazy_roundtrip: bool) -> pl.LazyFrame:
    """Create a LazyFrame, optionally via a lazy().collect() round-trip."""
    if lazy_roundtrip:
        return df.lazy().collect().lazy()
    return df.lazy()


def _to_dataframe(df: pl.DataFrame, lazy_roundtrip: bool) -> pl.DataFrame:
    """Create a DataFrame, optionally via a lazy().collect() round-trip."""
    if lazy_roundtrip:
        return df.lazy().collect()
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
def test_alifestd_has_contiguous_ids_polars_true(
    phylogeny_df, lazy_roundtrip
):
    """Verify returns True for datasets with contiguous ids."""
    df = _to_lazyframe(pl.from_pandas(phylogeny_df), lazy_roundtrip)
    assert alifestd_has_contiguous_ids_polars(df)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_alifestd_has_contiguous_ids_polars_false(
    phylogeny_df, lazy_roundtrip
):
    """Verify returns False for datasets with non-contiguous ids."""
    df = _to_lazyframe(pl.from_pandas(phylogeny_df), lazy_roundtrip)
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
    phylogeny_df, lazy_roundtrip
):
    """Verify polars result matches pandas result."""
    result_pd = alifestd_has_contiguous_ids(phylogeny_df)
    df = _to_lazyframe(pl.from_pandas(phylogeny_df), lazy_roundtrip)
    result_pl = alifestd_has_contiguous_ids_polars(df)
    assert result_pd == result_pl


def test_alifestd_has_contiguous_ids_polars_simple_true(lazy_roundtrip):
    """Ids 0, 1, 2 are contiguous."""
    df = _to_lazyframe(pl.DataFrame({"id": [0, 1, 2]}), lazy_roundtrip)
    assert alifestd_has_contiguous_ids_polars(df)


def test_alifestd_has_contiguous_ids_polars_simple_false_gap(lazy_roundtrip):
    """Ids 0, 2, 4 have gaps."""
    df = _to_lazyframe(pl.DataFrame({"id": [0, 2, 4]}), lazy_roundtrip)
    assert not alifestd_has_contiguous_ids_polars(df)


def test_alifestd_has_contiguous_ids_polars_simple_false_start(
    lazy_roundtrip,
):
    """Ids starting at 1 are not contiguous (must start at 0)."""
    df = _to_lazyframe(pl.DataFrame({"id": [1, 2, 3]}), lazy_roundtrip)
    assert not alifestd_has_contiguous_ids_polars(df)


def test_alifestd_has_contiguous_ids_polars_single_node(lazy_roundtrip):
    """Single node with id 0."""
    df = _to_lazyframe(pl.DataFrame({"id": [0]}), lazy_roundtrip)
    assert alifestd_has_contiguous_ids_polars(df)


def test_alifestd_has_contiguous_ids_polars_single_node_nonzero(
    lazy_roundtrip,
):
    """Single node with id != 0."""
    df = _to_lazyframe(pl.DataFrame({"id": [5]}), lazy_roundtrip)
    assert not alifestd_has_contiguous_ids_polars(df)


def test_alifestd_has_contiguous_ids_polars_empty(lazy_roundtrip):
    """Empty dataframe."""
    df = _to_lazyframe(
        pl.DataFrame({"id": []}, schema={"id": pl.Int64}), lazy_roundtrip
    )
    assert alifestd_has_contiguous_ids_polars(df)
