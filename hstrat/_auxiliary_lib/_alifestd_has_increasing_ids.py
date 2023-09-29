import numpy as np
import pandas as pd

from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids


def alifestd_has_increasing_ids(phylogeny_df: pd.DataFrame) -> bool:
    """Do offspring have larger id values than ancestors?

    Input dataframe is not mutated by this operation.
    """
    if "ancestor_id" in phylogeny_df:
        return np.all(phylogeny_df["id"] >= phylogeny_df["ancestor_id"])
    else:
        for _idx, row in phylogeny_df.iterrows():
            ancestor_list = alifestd_parse_ancestor_ids(row["ancestor_list"])
            if len(ancestor_list) == 0:
                continue
            elif max(ancestor_list) > row["id"]:
                return False

        return True
