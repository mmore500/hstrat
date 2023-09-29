import pandas as pd


def alifestd_make_empty(ancestor_id: bool = False) -> pd.DataFrame:
    """Create an alife standard phylogeny dataframe with zero rows."""
    res = pd.DataFrame(
        {
            "ancestor_list": pd.Series(dtype="str"),
            "id": pd.Series(dtype="int"),
        }
    )
    if ancestor_id:
        res["ancestor_id"] = pd.Series(dtype="int")
    return res
