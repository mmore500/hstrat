import pandas as pd

from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids


def alifestd_is_topologically_sorted(phylogeny_df: pd.DataFrame) -> bool:
    """Are all organisms listed after members of their `ancestor_list`?"""
    phylogeny_df = phylogeny_df.set_index("id", drop=False)

    for pos, (_idx, row) in enumerate(phylogeny_df.iterrows()):
        for ancestor_id in alifestd_parse_ancestor_ids(row["ancestor_list"]):
            if phylogeny_df.index.get_loc(ancestor_id) >= pos:
                return False

    return True
