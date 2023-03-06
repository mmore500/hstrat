import itertools as it
import warnings

import pandas as pd

from ._alifestd_is_asexual import alifestd_is_asexual
from ._alifestd_make_ancestor_list_col import alifestd_make_ancestor_list_col
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_splay_polytomies(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Use a simple splay strategy to resolve polytomies, converting them into
    bifurcations.

    For example,
    ```
      1
     /|\
    2 3 4
    ```
    becomes
    ```
      1
     / \
    2   5
       / \
      3   4
    ```

    No adjustments to any branch length columns in `phylogeny_df` are
    performed. However, `origin_time` (as well as all other columns) of a
    polytomy's parent node are duplicated in splayed-out nodes that resolve
    that polytomy. So, nodes added to perform the splaying-out will have zero-
    length subtending branches in this regard (i.e., their origin time will
    match their parent's).

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if "branch_length" in phylogeny_df or "edge_length" in phylogeny_df:
        warnings.warn(
            "alifestd_splay_polytomies does not update branch length columns. "
            "Use `origin_time` to recalculate branch lengths for collapsed "
            "phylogeny."
        )

    assert alifestd_is_asexual(phylogeny_df)

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    splay_to_lookup = dict()
    # splay_parent_lookup = {id_: id_ for id_ in phylogeny_df["id"]}
    splay_from_lookup = dict()
    phylogeny_df.set_index("id", drop=False, inplace=True)

    new_id_generator = it.count(phylogeny_df["id"].max() + 1)

    new_rows = dict()
    for id_, row in phylogeny_df.iterrows():
        ancestor_id = row["ancestor_id"]
        if ancestor_id == id_:  # root
            continue

        if ancestor_id not in splay_to_lookup:
            splayed_from_id = ancestor_id
            splayed_to_id = ancestor_id
        else:
            splayed_from_id = splay_to_lookup[ancestor_id]
            splayed_to_id = next(new_id_generator)

            phylogeny_df.loc[id_, "ancestor_id"] = splayed_to_id
            new_row = phylogeny_df.loc[ancestor_id].copy()
            new_row["id"] = splayed_to_id
            new_row["ancestor_id"] = splayed_from_id
            new_rows[splayed_to_id] = new_row

        splay_from_lookup[splayed_to_id] = splayed_from_id
        splay_to_lookup[ancestor_id] = splayed_to_id

    # drop unnecessary splays
    dropped_splay_remap = dict()
    for ancestor_id, splayed_to_id in splay_to_lookup.items():
        if ancestor_id != splayed_to_id:
            splayed_from_id = splay_from_lookup[splayed_to_id]
            assert new_rows[splayed_to_id]["ancestor_id"] == splayed_from_id
            dropped_splay_remap[splayed_to_id] = splayed_from_id
            del new_rows[splayed_to_id]

    # correct dropped splays
    phylogeny_df["ancestor_id"] = (
        phylogeny_df["ancestor_id"]
        .map(
            {
                **{
                    ancestor_id: ancestor_id
                    for ancestor_id in phylogeny_df["ancestor_id"]
                },
                **dropped_splay_remap,
            }
        )
        .astype(int)
    )

    appendum_df = pd.DataFrame(new_rows.values())
    phylogeny_df = pd.concat([phylogeny_df, appendum_df], ignore_index=True)

    phylogeny_df["ancestor_list"] = alifestd_make_ancestor_list_col(
        phylogeny_df["id"], phylogeny_df["ancestor_id"]
    )

    return phylogeny_df.reset_index(drop=True)
