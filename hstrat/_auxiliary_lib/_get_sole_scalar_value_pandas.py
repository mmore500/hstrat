import typing

import pandas as pd


def get_sole_scalar_value_pandas(
    df: pd.DataFrame, col_name: str
) -> typing.Any:
    """Get scalar value from DataFrame, ensuring it is unique."""
    values = df[col_name].unique()
    if len(values) != 1:
        raise ValueError(f"expected one {col_name} value, got {len(values)}")
    return values.squeeze()
