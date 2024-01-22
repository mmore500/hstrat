from collections import Counter

import pandas as pd

from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_count_polytomies(phylogeny_df: pd.DataFrame) -> int:
    """Count how many inner nodes have more than two descendant nodes.

    Only supports asexual phylogenies.
    """
    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df)
    if "ancestor_id" not in phylogeny_df.columns:
        raise ValueError(
            "alifestd_count_polytomies only supports asexual phylogenies.",
        )
    ancestor_counts = Counter(phylogeny_df["ancestor_id"])
    return sum(v > 2 for v in ancestor_counts.values())
