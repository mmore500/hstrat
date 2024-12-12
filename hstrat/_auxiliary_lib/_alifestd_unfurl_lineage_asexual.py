import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._unfurl_lineage_with_contiguous_ids import (
    unfurl_lineage_with_contiguous_ids,
)


def alifestd_unfurl_lineage_asexual(
    phylogeny_df: pd.DataFrame,
    leaf_id: int,
    mutate: bool = False,
) -> np.ndarray:
    """List `leaf_id` and its ancestor id sequence through tree root.

    The provided dataframe must be asexual.
    """

    phylogeny_df = alifestd_try_add_ancestor_id_col(
        phylogeny_df, mutate=mutate
    )
    if alifestd_has_contiguous_ids(phylogeny_df):
        return unfurl_lineage_with_contiguous_ids(
            phylogeny_df["ancestor_id"].to_numpy(dtype=np.uint64),
            int(leaf_id),
        )
    else:
        ancestor_lookup = dict(
            zip(phylogeny_df["id"], phylogeny_df["ancestor_id"])
        )
        cur_id = leaf_id
        res = []
        while True:
            res.append(cur_id)
            next_id = ancestor_lookup[cur_id]
            if next_id == cur_id:
                break
            cur_id = next_id

        return np.array(res)
