import typing

import numpy as np
import pandas as pd

from ._alifestd_categorize_triplet_asexual import (
    alifestd_categorize_triplet_asexual,
)
from ._alifestd_find_leaf_ids import alifestd_find_leaf_ids
from ._estimate_binomial_p import estimate_binomial_p


def alifestd_estimate_triplet_distance_asexual(
    first_df: pd.DataFrame,
    second_df: pd.DataFrame,
    taxon_label_key: str,
    confidence: float = 0.99,
    precision: float = 0.01,
    strict: typing.Union[bool, typing.Tuple[bool, bool]] = True,
    detail: bool = False,
    progress_wrap: typing.Callable = lambda x: x,
    mutate: bool = False,
) -> typing.Union[float, typing.Tuple[float, typing.Tuple[float, float, int]]]:
    """Estimate the triplet distance between two asexual phylogenetic trees in
    alife sampling sets of three leaf taxa and counting the fraction whose
    phylogenetic connectivity mismatch between trees.

    Parameters
    ----------
    first_df : pd.DataFrame
        The DataFrame representing the first phylogenetic tree.
    second_df : pd.DataFrame
        The DataFrame representing the second phylogenetic tree.
    taxon_label_key : str
        The key in the DataFrame to identify the taxon labels.
    confidence : float, default 0.99
        The confidence level for the estimation.

        See `estimate_binomial_p` for details.
    precision : float, default 0.01
        The precision of the estimation.

        See `estimate_binomial_p` for details.
    strict : bool or Tuple[bool, bool], default True
        A flag or a tuple of flags indicating how to treat tuples.

        If False, triplets that form a polytomy in either tree are not counted
        as mismatching. If True, they are counted as mismatching. If a tuple is
        given, polytomies in the first and second trees are treated according
        to the first and second elements of the tuple, respectively.
    detail : bool, default False
        If True, returns a detailed result including the estimated distance,
        confidence interval, and sample size.
    progress_wrap : typing.Callable, optional
        Pass tqdm or equivalent to display a progress bar.
    mutate : bool, default False
        If True, allows mutation of input DataFrames.

    Returns
    -------
    float or Tuple[float, Tuple[float, float, int]]
        The estimated distance between the two trees.

        If `detail` is True, returns a tuple containing the estimated distance,
        the confidence interval, and the sample size.

    Notes
    -----
    The core comparison is done by sampling triplets of taxa, categorizing
    them, and comparing these categorizations across the two trees, taking into
    account the `strict` and `lax` parameters for handling polytomies. See
    `alifestd_categorize_triplet_asexual` for details.

    See Also
    --------
    alifestd_categorize_triplet_asexual
    alifestd_sample_triplet_comparisons_asexual
    """
    if not mutate:
        first_df = first_df.copy()
        second_df = second_df.copy()
    try:
        strict1, strict2 = strict
    except TypeError:
        strict1 = strict2 = strict
        assert strict1 == strict2 == strict
    lax = (not bool(strict1), not bool(strict2))

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
        return (0.0, [0.0, 0.0], 0) if detail else 0.0

    def sample_triplet_comparison() -> bool:
        """Return True if the two categorizations differ."""
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

        polytomy = -1
        if cat1 == cat2:
            return False
        elif lax[0] and cat1 == polytomy:
            return False
        elif lax[1] and cat2 == polytomy:
            return False
        else:
            return True

    res = estimate_binomial_p(
        sample_triplet_comparison,
        confidence=confidence,
        precision=precision,
        progress_wrap=progress_wrap,
    )
    return res if detail else res[0]
