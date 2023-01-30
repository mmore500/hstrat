import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids
from ._jit import jit


@jit(nopython=True)
def _is_topologically_sorted(ancestor_ids: np.array) -> bool:
    for id, ancestor_id in enumerate(ancestor_ids):
        if id < ancestor_id:
            return False
    return True


def alifestd_is_topologically_sorted(phylogeny_df: pd.DataFrame) -> bool:
    """Are all organisms listed after members of their `ancestor_list`?"""

    if (
        alifestd_has_contiguous_ids(phylogeny_df)
        and "ancestor_id" in phylogeny_df
    ):
        return _is_topologically_sorted(phylogeny_df["ancestor_id"].to_numpy())

    phylogeny_df = phylogeny_df.set_index("id", drop=False)

    for pos, (_idx, row) in enumerate(phylogeny_df.iterrows()):
        for ancestor_id in alifestd_parse_ancestor_ids(row["ancestor_list"]):
            if phylogeny_df.index.get_loc(ancestor_id) >= pos:
                return False

    return True
