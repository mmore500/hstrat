import typing
import warnings

import polars as pl

from ._alifestd_check_topological_sensitivity_polars import (
    alifestd_check_topological_sensitivity_polars,
)


def alifestd_warn_topological_sensitivity_polars(
    phylogeny_df: typing.Union[pl.DataFrame, pl.LazyFrame],
    caller: str,
) -> None:
    """Emit a warning if `phylogeny_df` contains columns that may be
    invalidated by topological operations.

    Parameters
    ----------
    phylogeny_df : polars.DataFrame or polars.LazyFrame
        The phylogeny as a dataframe in alife standard format.
    caller : str
        Name of the calling function, included in the warning message.

    Input dataframe is not mutated by this operation.

    See Also
    --------
    alifestd_warn_topological_sensitivity :
        Pandas-based implementation.
    """
    present_warned = alifestd_check_topological_sensitivity_polars(
        phylogeny_df,
    )
    if present_warned:
        warnings.warn(
            f"{caller} does not update topology-dependent columns, "
            f"which may be invalidated: {present_warned}. "
            "Use `origin_time` to recalculate branch lengths for "
            "collapsed phylogeny. To silence this warning, use "
            "alifestd_drop_topological_sensitivity_polars."
        )
