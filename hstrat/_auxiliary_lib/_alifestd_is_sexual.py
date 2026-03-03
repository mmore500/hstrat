from deprecated.sphinx import deprecated
import pandas as pd


@deprecated(
    version="1.23.0",
    reason="Use phyloframe.legacy.alifestd_is_sexual instead.",
)
def alifestd_is_sexual(phylogeny_df: pd.DataFrame) -> bool:
    """Do any organisms in the phylogeny have than one immediate ancestor?

    Input dataframe is not mutated by this operation.
    """
    return phylogeny_df["ancestor_list"].astype("str").str.contains(",").any()
