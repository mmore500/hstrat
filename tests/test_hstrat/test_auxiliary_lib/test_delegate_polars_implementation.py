import os
import typing

import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    coerce_to_polars,
    delegate_polars_implementation,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@delegate_polars_implementation()
def dummy_func(
    df: pd.DataFrame, series: pd.Series
) -> typing.Tuple[pd.DataFrame, pd.Series]:
    assert isinstance(df, pd.DataFrame) and isinstance(series, pd.Series)
    return df, series


@pytest.mark.parametrize(
    "df",
    [
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
        coerce_to_polars(pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")),
        coerce_to_polars(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv")
        ),
        coerce_to_polars(
            pd.read_csv(f"{assets_path}/nk_tournamentselection.csv")
        ),
    ],
)
@pytest.mark.parametrize(
    "series",
    [
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")["id"],
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv")["origin_time"],
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv")["phenotype"],
        coerce_to_polars(
            pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")["id"]
        ),
        coerce_to_polars(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv")[
                "origin_time"
            ]
        ),
        coerce_to_polars(
            pd.read_csv(f"{assets_path}/nk_tournamentselection.csv")[
                "phenotype"
            ]
        ),
    ],
)
def test_coercion_and_error(
    df: typing.Union[pd.DataFrame, pl.DataFrame],
    series: typing.Union[pd.Series, pl.Series],
):
    if isinstance(df, pd.DataFrame) ^ isinstance(series, pd.Series):
        with pytest.raises(
            TypeError, match="mixing pandas and polars types is disallowed"
        ):
            dummy_func(df, series)
    else:
        new_df, new_series = dummy_func(df, series)
        assert type(new_df) == type(df)
        assert type(new_series) == type(series)


SignalException = type("", (Exception,), {})


def polars_func(df: pl.DataFrame):
    assert isinstance(df, pl.DataFrame)
    raise SignalException("Using polars function")


@delegate_polars_implementation(polars_func)
def pandas_func(df: pd.DataFrame):
    assert isinstance(df, pd.DataFrame)
    return df


@pytest.mark.parametrize(
    "df",
    [
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
        coerce_to_polars(pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")),
        coerce_to_polars(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv")
        ),
        coerce_to_polars(
            pd.read_csv(f"{assets_path}/nk_tournamentselection.csv")
        ),
    ],
)
def test_delegation(df: typing.Union[pd.DataFrame, pl.DataFrame]) -> None:
    if isinstance(df, pl.DataFrame):
        with pytest.raises(SignalException, match="Using polars function"):
            pandas_func(df)
    else:
        assert isinstance(pandas_func(df), pd.DataFrame)
