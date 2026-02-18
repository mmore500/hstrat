import typing

import polars as pl

from ._alifestd_check_topological_sensitivity import (
    _topologically_sensitive_cols,
)


def alifestd_check_topological_sensitivity_polars(
    phylogeny_df: typing.Union[pl.DataFrame, pl.LazyFrame],
) -> typing.List[str]:
    """Return names of columns present in `phylogeny_df` that may be
    invalidated by topological operations such as collapsing unifurcations.

    Accepts polars DataFrames and LazyFrames.

    Input dataframe is not mutated by this operation.

    See Also
    --------
    alifestd_check_topological_sensitivity :
        Pandas-based implementation.
    """
    if isinstance(phylogeny_df, pl.LazyFrame):
        columns = phylogeny_df.collect_schema().names()
    else:
        columns = phylogeny_df.columns
    return [
        col for col in columns if col in _topologically_sensitive_cols
    ]
