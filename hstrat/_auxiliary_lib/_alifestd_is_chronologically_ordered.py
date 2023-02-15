import numpy as np
import pandas as pd

from ._alifestd_has_compact_ids import alifestd_has_compact_ids
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids
from ._jit import jit
from ._jit_numpy_bool_t import jit_numpy_bool_t


@jit(nopython=True)
def _is_chronologically_ordered_contiguous(
    ancestor_ids: np.array, origin_times: np.array
) -> bool:
    for id_, ancestor_id in enumerate(ancestor_ids):
        # self comparison ok for geneses
        if origin_times[ancestor_id] > origin_times[id_]:
            return False
    return True


@jit(nopython=True)
def _is_chronologically_ordered_compact(
    ids: np.array, ancestor_ids: np.array, origin_times: np.array
) -> bool:
    origin_time_lookup = np.empty(len(ids))
    for (id_, origin_time) in zip(ids, origin_times):
        origin_time_lookup[id_] = origin_time

    for id_, ancestor_id in zip(ids, ancestor_ids):
        # self comparison ok for geneses
        if origin_time_lookup[ancestor_id] > origin_time_lookup[id_]:
            return False
    return True


@jit(nopython=True)
def _is_chronologically_ordered(
    ids: np.array, ancestor_ids: np.array, origin_times: np.array
) -> bool:
    origin_time_lookup = dict()
    for (id_, origin_time) in zip(ids, origin_times):
        origin_time_lookup[id_] = origin_time

    for id_, ancestor_id in zip(ids, ancestor_ids):
        # self comparison ok for geneses
        if origin_time_lookup[ancestor_id] > origin_time_lookup[id_]:
            return False
    return True


def alifestd_is_chronologically_ordered(phylogeny_df: pd.DataFrame) -> bool:
    """Are all organisms listed after members of their `ancestor_list`?

    Input dataframe is not mutated by this operation.
    """

    if "ancestor_id" in phylogeny_df:
        if alifestd_has_contiguous_ids(phylogeny_df):
            return _is_chronologically_ordered_contiguous(
                phylogeny_df["ancestor_id"].to_numpy(),
                phylogeny_df["origin_time"].to_numpy(),
            )
        elif alifestd_has_compact_ids(phylogeny_df):
            return _is_chronologically_ordered_compact(
                phylogeny_df["id"].to_numpy(),
                phylogeny_df["ancestor_id"].to_numpy(),
                phylogeny_df["origin_time"].to_numpy(),
            )
        else:
            return _is_chronologically_ordered(
                phylogeny_df["id"].to_numpy(),
                phylogeny_df["ancestor_id"].to_numpy(),
                phylogeny_df["origin_time"].to_numpy(),
            )

    phylogeny_df = phylogeny_df.set_index("id", drop=False)

    for _pos, (_idx, row) in enumerate(phylogeny_df.iterrows()):
        for ancestor_id in alifestd_parse_ancestor_ids(row["ancestor_list"]):
            ancestor_loc = phylogeny_df.index.get_loc(ancestor_id)
            if (
                phylogeny_df.iloc[ancestor_loc]["origin_time"]
                > row["origin_time"]
            ):
                return False

    return True
