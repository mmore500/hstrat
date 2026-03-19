from deprecated.sphinx import deprecated
import pandas as pd


@deprecated(
    version="1.23.0",
    reason="Use phyloframe.legacy.alifestd_make_empty instead.",
)
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
