import typing

import numpy as np
import pandas as pd

from ._alifestd_has_compact_ids import alifestd_has_compact_ids
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids
from ._jit import jit


@jit(nopython=True)
def _alifestd_find_chronological_inconsistency_contiguous(
    ancestor_ids: np.array, origin_times: np.array
) -> typing.Optional[int]:
    for id_, ancestor_id in enumerate(ancestor_ids):
        # self comparison ok for geneses
        if origin_times[ancestor_id] > origin_times[id_]:
            return id_
    return None


@jit(nopython=True)
def _alifestd_find_chronological_inconsistency_compact(
    ids: np.array, ancestor_ids: np.array, origin_times: np.array
) -> typing.Optional[int]:
    origin_time_lookup = np.empty(len(ids))
    for (id_, origin_time) in zip(ids, origin_times):
        origin_time_lookup[id_] = origin_time

    for id_, ancestor_id in zip(ids, ancestor_ids):
        # self comparison ok for geneses
        if origin_time_lookup[ancestor_id] > origin_time_lookup[id_]:
            return id_
    return None


@jit(nopython=True)
def _alifestd_find_chronological_inconsistency(
    ids: np.array, ancestor_ids: np.array, origin_times: np.array
) -> typing.Optional[int]:
    origin_time_lookup = dict()
    for (id_, origin_time) in zip(ids, origin_times):
        origin_time_lookup[id_] = origin_time

    for id_, ancestor_id in zip(ids, ancestor_ids):
        # self comparison ok for geneses
        if origin_time_lookup[ancestor_id] > origin_time_lookup[id_]:
            return id_
    return None


def alifestd_find_chronological_inconsistency(
    phylogeny_df: pd.DataFrame,
) -> typing.Optional[int]:
    """Return the id of a taxon with origin time precedint its parent's, if
    any are present."""

    if "ancestor_id" in phylogeny_df:
        if alifestd_has_contiguous_ids(phylogeny_df):
            return _alifestd_find_chronological_inconsistency_contiguous(
                phylogeny_df["ancestor_id"].to_numpy(),
                phylogeny_df["origin_time"].to_numpy(),
            )
        elif alifestd_has_compact_ids(phylogeny_df):
            return _alifestd_find_chronological_inconsistency_compact(
                phylogeny_df["id"].to_numpy(),
                phylogeny_df["ancestor_id"].to_numpy(),
                phylogeny_df["origin_time"].to_numpy(),
            )
        else:
            return _alifestd_find_chronological_inconsistency(
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
                return _idx

    return None
