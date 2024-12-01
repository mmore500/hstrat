import typing

import pandas as pd


def coerce_to_pandas(obj: typing.Any) -> typing.Any:
    """
    If a Pandas type is detected, coerces it to a Polars type.
    """
    if hasattr(obj, "__dataframe__"):
        return pd.api.interchange.from_dataframe(obj, allow_copy=False)
    elif hasattr(obj, "to_pandas"):
        return obj.to_pandas()  # pyarrow is required for this operation
    else:
        return obj
