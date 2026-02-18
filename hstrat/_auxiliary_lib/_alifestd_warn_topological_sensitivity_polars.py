import typing

import polars as pl

from ._alifestd_warn_topological_sensitivity import (
    _alifestd_warn_topological_sensitivity,
)


def alifestd_warn_topological_sensitivity_polars(
    phylogeny_df: typing.Union[pl.DataFrame, pl.LazyFrame],
    caller: str,
    *,
    insert: bool,
    delete: bool,
    update: bool,
) -> None:
    """Emit a warning if `phylogeny_df` contains columns that may be
    invalidated by topological operations.

    Parameters
    ----------
    phylogeny_df : polars.DataFrame or polars.LazyFrame
        The phylogeny as a dataframe in alife standard format.
    caller : str
        Name of the calling function, included in the warning message.
    insert : bool
        Whether the operation inserts new nodes.
    delete : bool
        Whether the operation deletes nodes.
    update : bool
        Whether the operation updates ancestor relationships.

    Input dataframe is not mutated by this operation.

    See Also
    --------
    alifestd_warn_topological_sensitivity :
        Pandas-based implementation.
    """
    _alifestd_warn_topological_sensitivity(
        phylogeny_df, caller,
        insert=insert, delete=delete, update=update,
    )
