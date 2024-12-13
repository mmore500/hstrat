import typing

import pandas as pd
import polars as pl

from ._coerce_to_pandas import _supported_iterables, _supported_mappings


def coerce_to_polars(obj: typing.Any, *, recurse: bool = False) -> typing.Any:
    """
    If a Pandas type is detected, coerce it to corresponding Polars type.
    """
    if isinstance(obj, (pd.Series, pd.DataFrame)):
        return pl.from_pandas(obj)
    elif recurse and isinstance(obj, _supported_iterables):
        return type(obj)(
            map(lambda x: coerce_to_polars(x, recurse=recurse), obj)
        )
    elif recurse and isinstance(obj, _supported_mappings):
        return {
            k: coerce_to_polars(v, recurse=recurse) for k, v in obj.items()
        }
    else:
        return obj
