import logging

from phyloframe import legacy as pfl
import polars as pl

from ._log_context_duration import log_context_duration


def alifestd_collapse_unifurcations_tallied_polars(
    phylogeny_df: pl.DataFrame,
    tally_col: str,
) -> pl.DataFrame:
    """Collapse unifurcations, tallying collapsed nodes into `tally_col`.

    Each remaining node's `tally_col` is incremented by the number of
    unifurcations collapsed between it and its new ancestor, including any
    previously tallied into those unifurcations.

    Parameters
    ----------
    phylogeny_df : pl.DataFrame
        The phylogeny as a dataframe in alife standard format.

        Must be asexual, with contiguous ids and topological sorting.
    tally_col : str
        Name of integer column holding tallies; must not contain nulls.

    Returns
    -------
    pl.DataFrame
        The phylogeny with unifurcations collapsed and tallies updated.

    See Also
    --------
    alifestd_collapse_unifurcations_tallied_asexual :
        Pandas-based implementation.
    """
    schema = phylogeny_df.lazy().collect_schema()
    null_count = phylogeny_df.lazy().select(pl.col(tally_col).null_count())
    assert null_count.collect().item() == 0

    tally = pl.col(tally_col)
    with log_context_duration(
        "alifestd_mark_unifurcation_length_polars", logging.info
    ):
        phylogeny_df = pfl.alifestd_mark_unifurcation_length_polars(
            phylogeny_df,
            mark_as="_alifestd_collapse_unifurcations_tallied_polars_tally_length",
            weights=tally + 1,
        )
    phylogeny_df = phylogeny_df.with_columns(
        (
            tally
            + pl.col(
                "_alifestd_collapse_unifurcations_tallied_polars_tally_length"
            )
        ).cast(schema[tally_col]),
    ).drop("_alifestd_collapse_unifurcations_tallied_polars_tally_length")

    with log_context_duration(
        "alifestd_collapse_unifurcations_polars", logging.info
    ):
        return pfl.alifestd_collapse_unifurcations_polars(phylogeny_df)
