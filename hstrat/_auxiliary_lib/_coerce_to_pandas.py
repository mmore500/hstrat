import typing

import pandas as pd


def coerce_to_pandas(obj: typing.Any) -> typing.Any:
    """
    If a Polars type is detected, coerce it to corresponding Pandas type.
    """
    if hasattr(obj, "__dataframe__"):
        return pd.api.interchange.from_dataframe(obj, allow_copy=True)
    elif hasattr(obj, "to_pandas"):
        return obj.to_pandas()  # pyarrow is required for this operation
    else:
        return obj
