from collections import defaultdict

import more_itertools as mit
import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_mark_origin_time_delta_asexual import (
    alifestd_mark_origin_time_delta_asexual,
)
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._alifestd_unfurl_traversal_postorder_asexual import (
    alifestd_unfurl_traversal_postorder_asexual,
)

_UNSAFE_SYMBOLS = (";", "(", ")", ",", "[", "]", ":", "'")


def alifestd_as_newick_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    *,
    label_key: str = "id",
    progress_wrap=lambda x: x,
) -> str:
    """Convert phylogeny dataframe to Newick format."""

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    if "origin_time_delta" in phylogeny_df.columns:
        pass
    elif "origin_time" in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_origin_time_delta_asexual(
            phylogeny_df, mutate=True
        )
    else:
        phylogeny_df["origin_time_delta"] = np.nan

    # adapted from https://github.com/niemasd/TreeSwift/blob/63b8979fb5e616ba89079d44e594682683c1365e/treeswift/Node.py#L129
    child_reps = defaultdict(list)
    postorder_ids = alifestd_unfurl_traversal_postorder_asexual(phylogeny_df)
    for id_ in progress_wrap(postorder_ids):

        if label_key is None:
            label = ""
        else:
            label = (
                id_ if label_key == "id" else phylogeny_df.at[id_, label_key]
            )
            label = f"{label}"
            if any(c in label for c in _UNSAFE_SYMBOLS):
                label = f"'{label}'"

        origin_time_delta = phylogeny_df.at[id_, "origin_time_delta"]

        if not np.isnan(origin_time_delta):
            label = f"{label}:{origin_time_delta}"
            if "." in label:
                label = label.rstrip("0").rstrip(".")

        children = child_reps.pop(id_, tuple())
        if children:
            label = f"({','.join(children)}){label}"

        ancestor_id = phylogeny_df.at[id_, "ancestor_id"]
        child_reps[ancestor_id].append(label)

    return ";\n".join(map(mit.one, child_reps.values())) + ";"
