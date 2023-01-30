import typing

import numpy as np
import opytional as opyt
import pandas as pd

from ._alifestd_make_ancestor_list_col import alifestd_make_ancestor_list_col
from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids
from ._jit import jit
from ._jit_numba_dict_t import jit_numba_dict_t
from ._jit_numpy_int64_t import jit_numpy_int64_t


@jit(nopython=True)
def _reassign_ids(
    ids: np.array,
    ancestor_ids: np.array,
) -> typing.Tuple[typing.Dict[int, int], np.array]:
    reassignment = jit_numba_dict_t.empty(
        key_type=jit_numpy_int64_t,
        value_type=jit_numpy_int64_t,
    )
    for id_ in ids:
        reassignment[id_] = len(reassignment)

    return reassignment, np.array(
        [reassignment[ancestor_id] for ancestor_id in ancestor_ids]
    )


def alifestd_assign_contiguous_ids(phylogeny_df: pd.DataFrame) -> pd.DataFrame:
    """TODO."""
    phylogeny_df = phylogeny_df.copy()

    reassignment, ancestor_ids = _reassign_ids(
        phylogeny_df["id"].to_numpy(dtype=np.int64),
        phylogeny_df["ancestor_id"].to_numpy(dtype=np.int64)
        if "ancestor_id" in phylogeny_df
        else np.array([], dtype=int),
    )

    phylogeny_df["id"] = np.arange(len(phylogeny_df))

    if len(ancestor_ids):
        phylogeny_df["ancestor_id"] = ancestor_ids
        phylogeny_df["ancestor_list"] = alifestd_make_ancestor_list_col(
            ancestor_ids
        )
    else:
        phylogeny_df["ancestor_list"] = phylogeny_df["ancestor_list"].map(
            lambda ancestor_list_str: str(
                [
                    reassignment[ancestor_id]
                    for ancestor_id in alifestd_parse_ancestor_ids(
                        ancestor_list_str
                    )
                ]
            )
        )
        phylogeny_df.loc[
            phylogeny_df["ancestor_list"] == "[]", "ancestor_list"
        ] = "[none]"

    return phylogeny_df
