import typing

import polars as pl

from ._alifestd_check_chronological_sensitivity import _get_sensitive_cols


def alifestd_check_chronological_sensitivity_polars(
    phylogeny_df: typing.Union[pl.DataFrame, pl.LazyFrame],
    *,
    shift: bool,
    rescale: bool,
    reassign: bool,
) -> typing.List[str]:
    """Return names of columns present in `phylogeny_df` that may be
    invalidated by chronological operations such as coercing chronological
    consistency.

    Accepts polars DataFrames and LazyFrames.

    If no such columns exist, returns an empty list.

    Parameters
    ----------
    phylogeny_df : polars.DataFrame or polars.LazyFrame
        The phylogeny as a dataframe in alife standard format.
    shift : bool
        Whether the operation shifts origin times by a constant offset.
    rescale : bool
        Whether the operation rescales origin times by a constant factor.
    reassign : bool
        Whether the operation arbitrarily reassigns origin times.

    Input dataframe is not mutated by this operation.

    See Also
    --------
    alifestd_check_chronological_sensitivity :
        Pandas-based implementation.
    """
    sensitive = _get_sensitive_cols(shift, rescale, reassign)
    columns = phylogeny_df.lazy().collect_schema().names()
    return [col for col in columns if col in sensitive]
