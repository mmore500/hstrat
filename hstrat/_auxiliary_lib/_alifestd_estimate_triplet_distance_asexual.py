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
    confidence: float = 0.99,
    precision: float = 0.01,
    strict: bool = True,
    detail: bool = False,
    progress_wrap: typing.Callable = lambda x: x,
) -> typing.Union[typing.Tuple[float, typing.Tuple[float, float, int]], float]:
    leaf_ids = alifestd_find_leaf_ids(first_df)
    assert set(leaf_ids) == set(alifestd_find_leaf_ids(second_df))

    if len(leaf_ids) < 3:
        return (0.0, [0.0, 0.0], 0) if detail else 0.0

    def sample_triplet_comparison() -> bool:
        triplet_ids = np.random.choice(leaf_ids, 3, replace=False)
        cat1 = alifestd_categorize_triplet_asexual(
            first_df, triplet_ids, mutate=True
        )
        cat2 = alifestd_categorize_triplet_asexual(
            second_df, triplet_ids, mutate=True
        )
        match = cat1 == cat2 or (not strict and -1 in (cat1, cat2))
        return not match

    res = estimate_binomial_p(
        sample_triplet_comparison,
        confidence=confidence,
        precision=precision,
        progress_wrap=progress_wrap,
    )
    return res if detail else res[0]
