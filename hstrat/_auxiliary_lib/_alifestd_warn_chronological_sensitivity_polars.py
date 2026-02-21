import typing

import polars as pl

from ._alifestd_check_chronological_sensitivity_polars import (
    alifestd_check_chronological_sensitivity_polars,
)
from ._alifestd_warn_chronological_sensitivity import (
    _alifestd_warn_chronological_sensitivity,
)


def alifestd_warn_chronological_sensitivity_polars(
    phylogeny_df: typing.Union[pl.DataFrame, pl.LazyFrame],
    caller: str,
    *,
    shift: bool,
    rescale: bool,
    reassign: bool,
) -> None:
    """Emit a warning if `phylogeny_df` contains columns that may be
    invalidated by chronological operations.

    Parameters
    ----------
    phylogeny_df : polars.DataFrame or polars.LazyFrame
        The phylogeny as a dataframe in alife standard format.
    caller : str
        Name of the calling function, included in the warning message.
    shift : bool
        Whether the operation shifts origin times by a constant offset.
    rescale : bool
        Whether the operation rescales origin times by a constant factor.
    reassign : bool
        Whether the operation arbitrarily reassigns origin times.

    Input dataframe is not mutated by this operation.

    See Also
    --------
    alifestd_warn_chronological_sensitivity :
        Pandas-based implementation.
    """
    _alifestd_warn_chronological_sensitivity(
        alifestd_check_chronological_sensitivity_polars(
            phylogeny_df,
            shift=shift,
            rescale=rescale,
            reassign=reassign,
        ),
        caller,
        shift=shift,
        rescale=rescale,
        reassign=reassign,
    )
