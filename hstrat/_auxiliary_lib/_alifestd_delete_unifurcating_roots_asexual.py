import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_asexual import alifestd_is_asexual
from ._alifestd_make_ancestor_list_col import alifestd_make_ancestor_list_col
from ._alifestd_mark_num_children_asexual import (
    alifestd_mark_num_children_asexual,
)
from ._alifestd_mark_roots import alifestd_mark_roots
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_delete_unifurcating_roots_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    root_ancestor_token: str = "none",
) -> pd.DataFrame:
    """Pare record to bypass root nodes with only one descendant.

    Dataframe reindexing (e.g., df.index) may be applied.

    See also `alifestd_collapse_unifurcations`.

    The option `root_ancestor_token` will be sandwiched in brackets to create
    the ancestor list entry for genesis organisms. For example, the token
    "None" will yield the entry "[None]" and the token "" will yield the entry
    "[]". Default "none".

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if not alifestd_is_asexual(phylogeny_df):
        raise ValueError("phylogeny_df must be strictly asexual")

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if "num_children" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_num_children_asexual(
            phylogeny_df, mutate=True
        )
    if "is_root" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_roots(phylogeny_df, mutate=True)

    phylogeny_df["is_unifurcating_root"] = (
        phylogeny_df["num_children"] == 1
    ) & phylogeny_df["is_root"]

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.set_index("id", drop=False, inplace=True)

    phylogeny_df["ancestor_is_unifurcating_root"] = phylogeny_df.loc[
        phylogeny_df["ancestor_id"].values, "is_unifurcating_root"
    ].values

    phylogeny_df.loc[
        phylogeny_df["ancestor_is_unifurcating_root"].values,
        "ancestor_id",
    ] = phylogeny_df.loc[
        phylogeny_df["ancestor_is_unifurcating_root"],
        "id",
    ].values

    phylogeny_df = phylogeny_df[~phylogeny_df["is_unifurcating_root"]].copy()

    if "ancestor_list" in phylogeny_df:
        phylogeny_df.loc[:, "ancestor_list"] = alifestd_make_ancestor_list_col(
            phylogeny_df["id"],
            phylogeny_df["ancestor_id"],
            root_ancestor_token=root_ancestor_token,
        )

    return phylogeny_df
