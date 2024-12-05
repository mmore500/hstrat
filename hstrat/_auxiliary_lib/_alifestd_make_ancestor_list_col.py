import pandas as pd

from ._alifestd_make_ancestor_list_col_polars import (
    alifestd_make_ancestor_list_col_polars,
)
from ._delegate_polars_implementation import (
    Series_T,
    delegate_polars_implementation,
)


@delegate_polars_implementation(alifestd_make_ancestor_list_col_polars)
def alifestd_make_ancestor_list_col(
    ids: Series_T,
    ancestor_ids: Series_T,
    root_ancestor_token: str = "none",
) -> Series_T:
    """Translate a column of integer ancestor id values into alife standard
    `ancestor_list` representation.

    The option `root_ancestor_token` will be sandwiched in brackets to create
    the ancestor list entry for genesis organisms. For example, the token
    "None" will yield the entry "[None]" and the token "" will yield the entry
    "[]". Default "none".
    """

    assert isinstance(ids, pd.Series) and isinstance(ancestor_ids, pd.Series)
    res = ancestor_ids.map("[{!s}]".format).astype(str)  # specify for empty
    res[ids == ancestor_ids] = f"[{root_ancestor_token}]"

    return res
