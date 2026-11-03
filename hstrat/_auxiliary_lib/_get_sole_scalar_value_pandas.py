import typing

import pandas as pd


def get_sole_scalar_value_pandas(
    df: pd.DataFrame, col_name: str
) -> typing.Any:
    """Get scalar value from DataFrame, ensuring it is unique.

    Raises ValueError if column `col_name` holds no values, or several
    distinct values.
    """
    return pd.unique(df[col_name]).item()
