import typing

import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_strictly_bifurcating_asexual import (
    alifestd_is_strictly_bifurcating_asexual,
)
from ._alifestd_mark_clade_logistic_growth_children_asexual import (
    alifestd_mark_clade_logistic_growth_children_asexual,
)
from ._alifestd_mark_is_left_child_asexual import (
    alifestd_mark_is_left_child_asexual,
)
from ._alifestd_mark_roots import alifestd_mark_roots
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_mark_clade_logistic_growth_sister_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    *,
    parallel_backend: typing.Optional[str] = None,
    progress_wrap: typing.Callable = lambda x: x,
    work_mask: typing.Optional[np.ndarray] = None,
) -> pd.DataFrame:
    """Add column `clade_logistic_growth_children`, containing the coefficient
    of a logistic regression fit to origin times of this clade's descendant
    leaves versus those of its sister clade.

    Clades with equal growth rate to their sister will have value approximately
    0.0. Clades growing faster than their sister clade will have value greater
    than 0.0. Clades growing slower than their sister clade will have value
    less than 0.0.

    Pass "loky" to `parallel_backend` to use joblib with loky backend.

    Root nodes will have value NaN. If provided, any nodes not included in
    `work_mask` will also have value NaN.

    Tree must be strictly bifurcating and single-rooted.

    Dataframe reindexing (e.g., df.index) may be applied.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.

    References
    ----------
    Bonetti Franceschi V and Volz E. Phylogenetic signatures reveal
        multilevel selection and fitness costs in SARS-CoV-2 [version 2; peer
        review: 2 approved, 1 approved with reservations]. Wellcome Open Res
        2024, 9:85 (https://doi.org/10.12688/wellcomeopenres.20704.2)

    Volz, E. Fitness, growth and transmissibility of SARS-CoV-2 genetic
        variants. Nat Rev Genet 24, 724-734 (2023).
        https://doi.org/10.1038/s41576-023-00610-z
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if work_mask is not None:
        work_mask = np.asarray(work_mask, dtype=bool)
        nowork_ids = phylogeny_df.loc[~work_mask, "id"].values

    if not alifestd_is_strictly_bifurcating_asexual(phylogeny_df):
        raise ValueError("phylogeny_df must be strictly bifurcating")

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)
    assert "ancestor_id" in phylogeny_df.columns

    if "clade_logistic_growth_children" not in phylogeny_df.columns:
        if work_mask is not None:
            work_ancestor_ids = phylogeny_df.loc[
                work_mask, "ancestor_id"
            ].values
            if alifestd_has_contiguous_ids(phylogeny_df):
                work_mask[:] = False
                work_mask[work_ancestor_ids] = True
            else:
                work_mask = phylogeny_df["id"].isin(work_ancestor_ids).values

        phylogeny_df = alifestd_mark_clade_logistic_growth_children_asexual(
            phylogeny_df,
            mutate=True,
            parallel_backend=parallel_backend,
            progress_wrap=progress_wrap,
            work_mask=work_mask,
        )

    if "is_left_child" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_is_left_child_asexual(
            phylogeny_df, mutate=True
        )

    if "is_root" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_roots(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    phylogeny_df["clade_logistic_growth_sister"] = phylogeny_df.loc[
        phylogeny_df["ancestor_id"], "clade_logistic_growth_children"
    ].values * (1 - 2 * phylogeny_df["is_left_child"].values)

    phylogeny_df.loc[
        phylogeny_df["is_root"].values, "clade_logistic_growth_sister"
    ] = np.nan

    if work_mask is not None:
        phylogeny_df.loc[nowork_ids, "clade_logistic_growth_sister"] = np.nan

    return phylogeny_df
