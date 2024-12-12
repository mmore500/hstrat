import operator

import numpy as np
import pandas as pd

from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._alifestd_unfurl_lineage_asexual import alifestd_unfurl_lineage_asexual


def alifestd_prune_extinct_lineages_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Drop taxa without extant descendants.

    An "extant" column, if provided, is used to determine extant taxa.
    Otherwise, taxa with inf or nan "destruction_time" are considered extant.

    Fastest with records in working format. See `alifestd_to_working_format`.

    Parameters
    ----------
    phylogeny_df : pandas.DataFrame
        The phylogeny as a dataframe in alife standard format.

        Must represent an asexual phylogeny.
    mutate : bool, default False
        Are side effects on the input argument `phylogeny_df` allowed?

    Raises
    ------
    ValueError
        If `phylogeny_df` has neither "extant" or "destruction_time" columns.

        Without at least one of these columns, which taxa are extant is
        ambiguous.

    Returns
    -------
    pandas.DataFrame
        The rerooted phylogeny in alife standard format.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)
    phylogeny_df.set_index("id", drop=False, inplace=True)

    extant_mask = None
    if "extant" in phylogeny_df:
        extant_mask = phylogeny_df["extant"]
    elif "destruction_time" in phylogeny_df:
        extant_mask = operator.or_(
            phylogeny_df["destruction_time"].isna(),
            np.isinf(phylogeny_df["destruction_time"]),
        )
    else:
        raise ValueError('Need "extant" or "destruction_time" column.')

    phylogeny_df["has_extant_descendant"] = False

    for extant_id in phylogeny_df.loc[extant_mask, "id"]:
        for lineage_id in alifestd_unfurl_lineage_asexual(
            phylogeny_df,
            int(extant_id),
            mutate=True,
        ):
            if phylogeny_df.loc[lineage_id, "has_extant_descendant"]:
                break

            phylogeny_df.loc[lineage_id, "has_extant_descendant"] = True

    drop_filter = ~phylogeny_df["has_extant_descendant"]
    phylogeny_df.drop(
        phylogeny_df.index[drop_filter], inplace=True, axis="rows"
    )
    phylogeny_df.drop("has_extant_descendant", inplace=True, axis="columns")
    return phylogeny_df.reset_index(drop=True)
