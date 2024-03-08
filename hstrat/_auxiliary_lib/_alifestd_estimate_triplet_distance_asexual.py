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
