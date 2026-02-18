import typing

import polars as pl

from ._alifestd_check_topological_sensitivity import _get_sensitive_cols


def alifestd_check_topological_sensitivity_polars(
    phylogeny_df: typing.Union[pl.DataFrame, pl.LazyFrame],
    *,
    insert: bool,
    delete: bool,
    update: bool,
) -> typing.List[str]:
    """Return names of columns present in `phylogeny_df` that may be
    invalidated by topological operations such as collapsing unifurcations.

    Accepts polars DataFrames and LazyFrames.

    Parameters
    ----------
    phylogeny_df : polars.DataFrame or polars.LazyFrame
        The phylogeny as a dataframe in alife standard format.
    insert : bool
        Whether the operation inserts new nodes.
    delete : bool
        Whether the operation deletes nodes.
    update : bool
        Whether the operation updates ancestor relationships.

    Input dataframe is not mutated by this operation.

    See Also
    --------
    alifestd_check_topological_sensitivity :
        Pandas-based implementation.
    """
    sensitive = _get_sensitive_cols(insert, delete, update)
    if isinstance(phylogeny_df, pl.LazyFrame):
        columns = phylogeny_df.collect_schema().names()
    else:
        columns = phylogeny_df.columns
    return [col for col in columns if col in sensitive]
