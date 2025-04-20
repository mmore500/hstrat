import typing

import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_mark_roots import alifestd_mark_roots
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_coarsen_taxa_asexual_make_agg(
    phylogeny_df: pd.DataFrame,
    default_agg: str = "first",
) -> typing.Dict[str, str]:
    """Build per-column aggregation rules for asexual taxa coarsening.

    Parameters
    ----------
    phylogeny_df : pd.DataFrame
        Input phylogeny table.
    default_agg : str, default "first"
        Aggregation function to apply to any column not in the hard-coded
        overrides.

    Returns
    -------
    Dict[str, str]
        Mapping of column name to aggregation method. Four columns are
        overridden as follows:

        - "branch_length": "sum"
        - "destruction_time": "last"
        - "edge_length": "sum"
        - "is_root": "first"
        - "origin_time": "first"

        Columns named

        - "ancestor_id"
        - "ancestor_list"
        - "id"
        - "is_leaf"

        will be excluded from the result. All other (non-excluded) columns use
        `default_agg`.
    """
    overrides = {
        "branch_length": "sum",
        "destruction_time": "last",
        "edge_length": "sum",
        "is_root": "first",
        "origin_time": "first",
    }
    return {
        col: overrides.get(col, default_agg)
        for col in phylogeny_df.columns
        if col
        not in (
            "ancestor_id",
            "ancestor_list",
            "id",
            "is_leaf",
        )
    }


def alifestd_coarsen_taxa_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    *,
    agg: typing.Optional[typing.Dict[str, str]] = None,
    by: typing.Union[str, typing.Sequence[str]],
) -> pd.DataFrame:
    """Pare record to bypass organisms outside mask.

    The root ancestor token will be adopted from phylogeny_df.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if "is_root" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_roots(phylogeny_df, mutate=True)

    if agg is None:
        agg = alifestd_coarsen_taxa_asexual_make_agg(phylogeny_df)

    if "id" in agg:
        raise ValueError("agg for `id` column may not be overwritten")
    agg["id"] = "last"

    if "ancestor_id" in agg:
        raise ValueError("agg for `ancestor_id` column may not be overwritten")
    agg["ancestor_id"] = "first"

    if "ancestor_list" in agg:
        raise ValueError(
            "agg for `ancestor_list` column may not be overwritten"
        )
    agg["ancestor_list"] = "first"

    if isinstance(by, str):
        by = (by,)

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.set_index("id", drop=False, inplace=True)

    phylogeny_df[
        "alifestd_coarsen_taxa_asexual_is_taxon_founder"
    ] = np.logical_or.reduce(
        phylogeny_df.loc[:, by].values.T
        != phylogeny_df.loc[phylogeny_df["ancestor_id"].values, by].values.T
    ) | (
        phylogeny_df["is_root"].values
    )

    phylogeny_df[
        "alifestd_coarsen_taxa_asexual_taxon_ancestor_id"
    ] = phylogeny_df["ancestor_id"]
    phylogeny_df[
        "alifestd_coarsen_taxa_asexual_taxon_founder_id"
    ] = phylogeny_df["id"]

    for idx in phylogeny_df.index:
        if phylogeny_df.at[
            idx, "alifestd_coarsen_taxa_asexual_is_taxon_founder"
        ]:
            continue

        ancestor_id = phylogeny_df.at[idx, "ancestor_id"]
        phylogeny_df.at[
            idx, "alifestd_coarsen_taxa_asexual_taxon_founder_id"
        ] = phylogeny_df.at[
            ancestor_id, "alifestd_coarsen_taxa_asexual_taxon_founder_id"
        ]

        ancestor_taxon_ancestor_id = phylogeny_df.at[
            ancestor_id, "alifestd_coarsen_taxa_asexual_taxon_ancestor_id"
        ]
        phylogeny_df.at[
            idx, "alifestd_coarsen_taxa_asexual_taxon_ancestor_id"
        ] = (
            ancestor_taxon_ancestor_id
            if not phylogeny_df.at[ancestor_taxon_ancestor_id, "is_root"]
            else idx
        )

    phylogeny_df = phylogeny_df.groupby(
        "alifestd_coarsen_taxa_asexual_taxon_founder_id",
        as_index=False,
        observed=True,
    ).agg(agg)

    return phylogeny_df.drop(
        [
            "alifestd_coarsen_taxa_asexual_taxon_ancestor_id",
            "alifestd_coarsen_taxa_asexual_taxon_founder_id",
            "alifestd_coarsen_taxa_asexual_is_taxon_founder",
        ],
        axis="columns",
        errors="ignore",
    ).reset_index(drop=True)
