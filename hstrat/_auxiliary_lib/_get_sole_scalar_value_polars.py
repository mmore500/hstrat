import typing

import polars as pl


def get_sole_scalar_value_polars(
    df: pl.DataFrame, col_name: str
) -> typing.Any:
    """Get scalar value from DataFrame, ensuring it is unique."""
    if df.lazy().limit(1).collect().is_empty():
        raise ValueError(f"DataFrame is empty, cannot get {col_name}")
    dtype = df.lazy().collect_schema()[col_name]
    if dtype.is_numeric():
        is_unique = (
            df.lazy()
            .filter(pl.col(col_name).diff() != pl.lit(0))
            .limit(1)
            .collect()
            .is_empty()
        )
    else:  # e.g., strings or categoricals, which lack diff
        is_unique = (
            df.lazy().select(pl.col(col_name).n_unique()).collect().item() == 1
        )
    if not is_unique:
        raise ValueError(f"multiple {col_name} values detected")
    return df.lazy().select(col_name).limit(1).collect().item()
