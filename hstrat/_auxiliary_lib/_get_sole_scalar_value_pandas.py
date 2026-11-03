import typing

import pandas as pd


def get_sole_scalar_value_pandas(
    df: pd.DataFrame, col_name: str
) -> typing.Any:
    """Get scalar value from DataFrame, ensuring it is unique."""
    if df.empty:
        raise ValueError(f"DataFrame is empty, cannot get {col_name}")
    values = df[col_name].unique()
    if len(values) > 1:
        raise ValueError(f"multiple {col_name} values detected")
    return values[0]
