import typing

import pandas as pd

_supported_iterables = tuple, set, list, frozenset
_supported_mappings = dict


def coerce_to_pandas(obj: typing.Any) -> typing.Any:
    """
    If a Polars type is detected, coerce it to corresponding Pandas type.
    """
    if isinstance(obj, _supported_iterables):
        return type(obj)(coerce_to_pandas(ele) for ele in obj)
    elif isinstance(obj, _supported_mappings):  # includes defaultdict etc
        return type(obj)({k: coerce_to_pandas(v) for k, v in obj.items()})
    elif hasattr(obj, "__dataframe__"):
        return pd.api.interchange.from_dataframe(obj, allow_copy=True)
    elif hasattr(obj, "to_pandas"):
        return obj.to_pandas()  # pyarrow is required for this operation
    else:
        return obj
