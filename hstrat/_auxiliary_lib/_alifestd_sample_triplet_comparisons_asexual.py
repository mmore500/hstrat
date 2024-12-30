import typing

import numpy as np
import pandas as pd

from ._alifestd_categorize_triplet_asexual import (
    alifestd_categorize_triplet_asexual,
)
from ._alifestd_find_leaf_ids import alifestd_find_leaf_ids
from ._alifestd_find_mrca_id_asexual import alifestd_find_mrca_id_asexual


def alifestd_sample_triplet_comparisons_asexual(
    first_df: pd.DataFrame,
    second_df: pd.DataFrame,
    taxon_label_key: str,
    n: int = 1000,
    progress_wrap: typing.Callable = lambda x: x,
    mutate: bool = False,
) -> pd.DataFrame:
    """Sample triplet comparisons between two asexual phylogenetic trees in
    alife standard form, creating a DataFrame with the triplet categorizations
    and comparison results as well as corresponding data from MRCA row within
    the first tree.

    The MRCA row corresponds to the most recent common ancestor of two of the
    three taxa in the triplet.

    Parameters
    ----------
    first_df : pd.DataFrame
        The DataFrame representing the first phylogenetic tree.
    second_df : pd.DataFrame
        The DataFrame representing the second phylogenetic tree.
    taxon_label_key : str
        The key in the DataFrame to identify the taxon labels.
    n : int, default 1000
        The number of samples to take.

        Corresponds to number of rows in the returned DataFrame.
    progress_wrap : typing.Callable, optional
        Pass tqdm or equivalent to display a progress bar.
    mutate : bool, default False
        If True, allows mutation of input DataFrames.

    Returns
    -------
    pd.DataFrame
        A DataFrame with rows corresponding to sampled triplet comparisons and
        the following columns:
        - "triplet code, {first,second}": the categorization of the triplet in
          the first or second tree.
        - "triplet match, {lax,lax/strict,strict,strict/lax}": whether the
          triplet categorizations match with differing treatment of polytomies.
        - all columns from the first tree.

    Notes
    -----
    The core comparison is done by sampling triplets of taxa, categorizing
    them, and comparing these categorizations across the two trees, taking into
    account the `strict` and `lax` parameters for handling polytomies. See
    `alifestd_categorize_triplet_asexual` for details.

    See Also
    --------
    alifestd_categorize_triplet_asexual
    alifestd_estimate_triplet_distance_asexual
    """
    if not mutate:
        first_df = first_df.copy()
        second_df = second_df.copy()

    first_df = first_df.reset_index(drop=True).set_index("id", drop=False)
    second_df = second_df.reset_index(drop=True).set_index("id", drop=False)

    first_leaf_ids = alifestd_find_leaf_ids(first_df)
    first_taxon_labels = first_df.loc[first_leaf_ids, taxon_label_key]
    second_leaf_ids = alifestd_find_leaf_ids(second_df)
    second_taxon_labels = second_df.loc[second_leaf_ids, taxon_label_key]

    assert first_taxon_labels.is_unique
    assert second_taxon_labels.is_unique
    assert (
        first_taxon_labels.sort_values().to_numpy()
        == second_taxon_labels.sort_values().to_numpy()
    ).all()

    if len(first_leaf_ids) < 3:
        raise ValueError("Too few leaves to sample any triplets.")

    def sample_triplet_comparison() -> dict:
        """Sample details of one triplet comparison between trees."""
        labels = np.random.choice(first_taxon_labels, 3, replace=False)
        first_triplet_ids = [
            first_df.index[first_df[taxon_label_key] == label].item()
            for label in labels
        ]
        second_triplet_ids = [
            second_df.index[second_df[taxon_label_key] == label].item()
            for label in labels
        ]
        assert 3 == len(first_triplet_ids) == len(second_triplet_ids)

        cat1 = alifestd_categorize_triplet_asexual(
            first_df, first_triplet_ids, mutate=True
        )
        cat2 = alifestd_categorize_triplet_asexual(
            second_df, second_triplet_ids, mutate=True
        )

        first_sampled_leaf_pair = np.random.choice(
            first_triplet_ids, 2, replace=False
        )
        sampled_mrca_id = alifestd_find_mrca_id_asexual(
            first_df, first_sampled_leaf_pair, mutate=True
        )
        polytomy = -1
        return {
            "triplet code, first": cat1,
            "triplet code, second": cat2,
            "triplet match, lax": (
                (cat1 == cat2) or (cat1 == polytomy) or (cat2 == polytomy)
            ),
            "triplet match, lax/strict": (cat1 == cat2) or (cat1 == polytomy),
            "triplet match, strict": cat1 == cat2,
            "triplet match, strict/lax": (cat1 == cat2) or (cat2 == polytomy),
            **first_df.loc[sampled_mrca_id].to_dict(),
        }

    return pd.DataFrame.from_records(
        [sample_triplet_comparison() for _ in progress_wrap(range(n))],
    )
