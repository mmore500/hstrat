import pandas as pd


def swap_rows_and_indices(df: pd.DataFrame, loc1, loc2) -> pd.DataFrame:
    """Swap positions of indices `loc1` and `loc2` and their corresponding
    rows."""
    indices = [*df.index]
    iloc1 = df.index.get_loc(loc1)
    iloc2 = df.index.get_loc(loc2)
    indices[iloc1], indices[iloc2] = indices[iloc2], indices[iloc1]
    return df.loc[indices]
