import typing

import pandas as pd
import polars as pl

from ._coerce_to_pandas import _supported_iterables, _supported_mappings


def coerce_to_polars(obj: typing.Any) -> typing.Any:
    """
    If a Pandas type is detected, coerce it to corresponding Polars type.
    """
    if isinstance(obj, _supported_iterables):
        return type(obj)(map(coerce_to_polars, obj))
    elif isinstance(obj, _supported_mappings):
        return {k: coerce_to_polars(v) for k, v in obj.items()}
    elif isinstance(obj, (pd.Series, pd.DataFrame)):
        return pl.from_pandas(obj)
    return obj
