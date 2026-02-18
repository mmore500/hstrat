import typing
import warnings

import pandas as pd

from ._alifestd_find_root_ids import alifestd_find_root_ids


_warned_columns = (
    "ancestor_origin_time",
    "branch_length",
    "clade_duration",
    "clade_duration_ratio_sister",
    "clade_fblr_growth_children",
    "clade_fblr_growth_sister",
    "clade_faithpd",
    "clade_leafcount_ratio_sister",
    "clade_logistic_growth_children",
    "clade_logistic_growth_sister",
    "clade_nodecount_ratio_sister",
    "clade_subtended_duration",
    "clade_subtended_duration_ratio_sister",
    "edge_length",
    "is_left_child",
    "is_right_child",
    "left_child_id",
    "max_descendant_origin_time",
    "node_depth",
    "num_children",
    "num_descendants",
    "num_leaves",
    "num_leaves_sibling",
    "num_preceding_leaves",
    "origin_time_delta",
    "ot_mrca_id",
    "ot_mrca_time_of",
    "ot_mrca_time_since",
    "right_child_id",
    "sister_id",
)


def alifestd_add_global_root(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    origin_time: typing.Optional[float] = None,
) -> pd.DataFrame:
    """Add a new global root node that all existing roots point to.

    The new root node will only have columns `id`, `ancestor_id` (if
    applicable), `ancestor_list` (if applicable), and `origin_time` (if
    applicable). All other columns will be NaN for the new root row.

    Parameters
    ----------
    phylogeny_df : pd.DataFrame
        Phylogeny dataframe in alife standard format.
    mutate : bool, default False
        If True, allows mutation of the input dataframe.
    origin_time : float or None, default None
        If provided, sets the `origin_time` of the new global root node.

    Returns
    -------
    pd.DataFrame
        The phylogeny dataframe with a new global root added.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if len(phylogeny_df) == 0:
        return phylogeny_df

    # Warn about columns that may become invalid
    present_warned = [
        col for col in _warned_columns if col in phylogeny_df
    ]
    if present_warned:
        warnings.warn(
            "alifestd_add_global_root does not update columns "
            f"{present_warned}. These columns may become invalid after "
            "adding a global root."
        )

    # Create new root id
    new_root_id = phylogeny_df["id"].max() + 1

    # Build the new root row with only applicable columns
    new_root = {"id": new_root_id}

    if "ancestor_id" in phylogeny_df:
        new_root["ancestor_id"] = new_root_id

    if "ancestor_list" in phylogeny_df:
        new_root["ancestor_list"] = "[none]"

    if origin_time is not None:
        new_root["origin_time"] = origin_time

    # Point existing roots to the new global root
    root_ids = alifestd_find_root_ids(phylogeny_df)
    root_mask = phylogeny_df["id"].isin(root_ids)

    if "ancestor_id" in phylogeny_df:
        phylogeny_df.loc[root_mask, "ancestor_id"] = new_root_id

    if "ancestor_list" in phylogeny_df:
        phylogeny_df.loc[root_mask, "ancestor_list"] = f"[{new_root_id}]"

    # Append the new root row
    new_root_df = pd.DataFrame([new_root])
    res = pd.concat([phylogeny_df, new_root_df], ignore_index=True)

    return res
