import typing

import pandas as pd
import polars as pl


def coerce_to_polars(arg: typing.Any) -> typing.Any:
    """
    If a Pandas type is detected, coerce it to corresponding Polars type.
    """
    if isinstance(arg, (pd.Series, pd.DataFrame)):
        return pl.from_pandas(arg)
    return arg
