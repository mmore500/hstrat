import logging

import pandas as pd
from phyloframe import legacy as pfl

from ._log_context_duration import log_context_duration


def alifestd_collapse_unifurcations_tallied_asexual(
    phylogeny_df: pd.DataFrame,
    tally_col: str,
    *,
    mutate: bool = False,
) -> pd.DataFrame:
    """Collapse unifurcations, tallying collapsed nodes into `tally_col`.

    Each remaining node's `tally_col` is incremented by the number of
    unifurcations collapsed between it and its new ancestor, including any
    previously tallied into those unifurcations.

    Parameters
    ----------
    phylogeny_df : pd.DataFrame
        The phylogeny as a dataframe in alife standard format.

        Must be asexual, with contiguous ids and topological sorting.
    tally_col : str
        Name of integer column holding tallies; must not contain NaN.
    mutate : bool, default False
        Are side effects on the input argument `phylogeny_df` allowed?

    Returns
    -------
    pd.DataFrame
        The phylogeny with unifurcations collapsed and tallies updated.

    See Also
    --------
    alifestd_collapse_unifurcations_tallied_polars :
        Polars-based implementation.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    assert not phylogeny_df[tally_col].isna().any()

    phylogeny_df["_tally_weight"] = phylogeny_df[tally_col] + 1
    with log_context_duration(
        "alifestd_mark_unifurcation_length_asexual", logging.info
    ):
        phylogeny_df = pfl.alifestd_mark_unifurcation_length_asexual(
            phylogeny_df,
            mutate=True,
            mark_as="_tally_length",
            weights="_tally_weight",
        )
    phylogeny_df[tally_col] = (
        phylogeny_df[tally_col] + phylogeny_df["_tally_length"]
    ).astype(phylogeny_df[tally_col].dtype)
    phylogeny_df.drop(columns=["_tally_length", "_tally_weight"], inplace=True)

    with log_context_duration("alifestd_collapse_unifurcations", logging.info):
        return pfl.alifestd_collapse_unifurcations(phylogeny_df, mutate=True)
