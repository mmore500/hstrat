import polars as pl


def get_sole_scalar_value_polars(df: pl.DataFrame, col_name: str) -> int:
    """Get scalar value from DataFrame, ensuring it is unique."""
    if df.lazy().limit(1).collect().is_empty():
        raise ValueError(f"DataFrame is empty, cannot get {col_name}")
    if (
        not df.lazy()
        .filter(pl.col(col_name).diff() != pl.lit(0))
        .limit(1)
        .collect()
        .is_empty()
    ):
        raise ValueError(f"multiple {col_name} values detected")
    return df.lazy().select(col_name).limit(1).collect().item()
