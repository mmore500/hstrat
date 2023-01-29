import pandas as pd

from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids


def alifestd_is_disconnected(phylogeny_df: pd.DataFrame) -> bool:
    return (
        (phylogeny_df["ancestor_list"] == "[]").sum()
        + (phylogeny_df["ancestor_list"] == "[NONE]").sum()
        + (phylogeny_df["ancestor_list"] == "[none]").sum()
        + (phylogeny_df["ancestor_list"] == "[None]").sum()
    ) >= 2
