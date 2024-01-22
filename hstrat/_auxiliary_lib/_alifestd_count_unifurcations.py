from collections import Counter

import pandas as pd

from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_count_unifurcations(phylogeny_df: pd.DataFrame) -> int:
    """Count how many inner nodes have exactly one descendant node.

    Only supports asexual phylogenies.
    """
    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df)
    if "ancestor_id" not in phylogeny_df.columns:
        raise ValueError(
            "alifestd_count_unifurcations only supports asexual phylogenies.",
        )
    except_roots = phylogeny_df["ancestor_id"] != phylogeny_df["id"]
    ancestor_counts = Counter(phylogeny_df.loc[except_roots, "ancestor_id"])
    return sum(v == 1 for v in ancestor_counts.values())
