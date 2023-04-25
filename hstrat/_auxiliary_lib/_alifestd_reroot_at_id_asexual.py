import warnings

import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_make_ancestor_list_col import alifestd_make_ancestor_list_col
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._alifestd_unfurl_lineage_asexual import alifestd_unfurl_lineage_asexual
from ._pairwise import pairwise


def alifestd_reroot_at_id_asexual(
    phylogeny_df: pd.DataFrame,
    new_root_id: int,
    mutate: bool = False,
) -> pd.DataFrame:
    """Reroot phylogeny, preserving topology.

    Reverses the descendant-to-ancestor relationships of all ancestors of the
    new root. Does not update branch_lengths or edge_lengths columns if
    present.

    Parameters
    ----------
    phylogeny_df : pandas.DataFrame
        The phylogeny as a dataframe in alife standard format.

        Must represent an asexual phylogeny.
    new_root_id : int
        The ID of the node to use as the new root of the phylogeny.
    mutate : bool, default False
        Are side effects on the input argument `phylogeny_df` allowed?

    Returns
    -------
    pandas.DataFrame
        The rerooted phylogeny in alife standard format.
    """

    if "branch_length" in phylogeny_df or "edge_length" in phylogeny_df:
        warnings.warn(
            "alifestd_reroot_at_id_asexual does not update branch length "
            "columns. Use `origin_time` to recalculate branch lengths for "
            "rerooted phylogeny."
        )

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)
    unfurled_lineage = alifestd_unfurl_lineage_asexual(
        phylogeny_df, new_root_id
    )

    # contiguous id implementation
    if alifestd_has_contiguous_ids(phylogeny_df):
        copy_to_slice = unfurled_lineage[1:]
        copy_from_slice = unfurled_lineage[:-1]
        phylogeny_df["ancestor_id"].to_numpy()[copy_to_slice] = phylogeny_df[
            "id"
        ].to_numpy()[copy_from_slice]

        phylogeny_df["ancestor_id"].to_numpy()[new_root_id] = phylogeny_df[
            "id"
        ].to_numpy()[new_root_id]

    # noncontiguous id implementation
    else:
        iloc_lookup = dict(
            zip(phylogeny_df["id"], np.arange(len(phylogeny_df)))
        )
        for ancestor_id, descendant_id in pairwise(reversed(unfurled_lineage)):
            iloc = iloc_lookup[ancestor_id]
            phylogeny_df["ancestor_id"].to_numpy()[iloc] = descendant_id

        new_root_iloc = iloc_lookup[new_root_id]
        phylogeny_df["ancestor_id"].to_numpy()[new_root_iloc] = phylogeny_df[
            "id"
        ].to_numpy()[new_root_iloc]

    # update ancestor list
    phylogeny_df["ancestor_list"] = alifestd_make_ancestor_list_col(
        phylogeny_df["id"],
        phylogeny_df["ancestor_id"],
    )
    return phylogeny_df
