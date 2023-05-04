import pandas as pd


def alifestd_make_empty() -> pd.DataFrame:
    """Create an alife standard phylogeny dataframe with zero rows."""
    return pd.DataFrame(
        {
            "ancestor_list": pd.Series(dtype="str"),
            "id": pd.Series(dtype="int"),
        }
    )
