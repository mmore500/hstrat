import types
import typing

import pandas as pd

from ._alifestd_find_root_ids import alifestd_find_root_ids
from ._alifestd_warn_topological_sensitivity import (
    alifestd_warn_topological_sensitivity,
)


def alifestd_add_global_root(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    root_attrs: typing.Mapping[str, typing.Any] = types.MappingProxyType({}),
) -> pd.DataFrame:
    """Add a new global root node that all existing roots point to.

    The new root node will have columns `id`, `ancestor_id` (if applicable),
    `ancestor_list` (if applicable), and any columns specified in
    `root_attrs`. All other columns will be NaN for the new root row.

    Parameters
    ----------
    phylogeny_df : pd.DataFrame
        Phylogeny dataframe in alife standard format.
    mutate : bool, default False
        If True, allows mutation of the input dataframe.
    root_attrs : Mapping[str, Any], default {}
        Column values to set on the new global root row, e.g.,
        ``{"origin_time": 0.0, "taxon_label": "root"}``.

        Keys ``"id"``, ``"ancestor_id"``, and ``"ancestor_list"`` are
        reserved and may not be specified; a `ValueError` is raised if
        any are present.

    Returns
    -------
    pd.DataFrame
        The phylogeny dataframe with a new global root added.

    Raises
    ------
    ValueError
        If `root_attrs` contains reserved keys.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """
    _reserved = {"id", "ancestor_id", "ancestor_list"}
    bad_keys = _reserved & root_attrs.keys()
    if bad_keys:
        raise ValueError(
            f"root_attrs must not contain reserved keys {bad_keys}; "
            "these are set automatically"
        )

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    # Create new root id
    new_root_id = (
        phylogeny_df["id"].max() + 1 if len(phylogeny_df) else 0
    )

    alifestd_warn_topological_sensitivity(
        phylogeny_df,
        "alifestd_add_global_root",
        insert=True,
        delete=False,
        update=True,
    )

    # Build the new root row with only applicable columns
    new_root = {"id": new_root_id}

    if "ancestor_id" in phylogeny_df:
        new_root["ancestor_id"] = new_root_id

    if "ancestor_list" in phylogeny_df:
        new_root["ancestor_list"] = "[none]"

    new_root.update(root_attrs)

    # Point existing roots to the new global root
    root_ids = alifestd_find_root_ids(phylogeny_df)
    root_mask = phylogeny_df["id"].isin(root_ids)

    if "ancestor_id" in phylogeny_df:
        phylogeny_df.loc[root_mask, "ancestor_id"] = new_root_id

    if "ancestor_list" in phylogeny_df:
        phylogeny_df.loc[root_mask, "ancestor_list"] = f"[{new_root_id}]"

    # Append the new root row (vertical concat; mismatched columns get NaN)
    new_root_df = pd.DataFrame([new_root])
    res = pd.concat([phylogeny_df, new_root_df], axis=0, ignore_index=True)

    return res
