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


@delegate_polars_implementation(recurse_type_checks=True)
def dummy_func(
    df_dict: dict[str, pd.DataFrame],
    series_list_singleton: typing.List[pd.Series],
    dummy_val: typing.Any,
) -> typing.Tuple[pd.DataFrame, pd.Series, typing.Any]:
    assert isinstance(df_dict["df"], pd.DataFrame) and isinstance(
        series_list_singleton[0], pd.Series
    )
    return df_dict["df"], series_list_singleton[0], dummy_val


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
        coerce_to_polars(
            pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")
        ).lazy(),
        coerce_to_polars(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv")
        ).lazy(),
        coerce_to_polars(
            pd.read_csv(f"{assets_path}/nk_tournamentselection.csv")
        ).lazy(),
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
            dummy_func({"df": df}, [series], 1234)
    else:
        new_df, new_series, _ = dummy_func({"df": df}, [series], "asdf")
        assert isinstance(new_df, type(df)) or isinstance(
            new_df, type(df.collect())
        )
        assert isinstance(new_series, type(series))


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
