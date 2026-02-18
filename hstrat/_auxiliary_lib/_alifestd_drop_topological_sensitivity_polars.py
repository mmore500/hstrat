import polars as pl

from ._alifestd_check_topological_sensitivity import (
    alifestd_check_topological_sensitivity,
)


def alifestd_drop_topological_sensitivity_polars(
    phylogeny_df: pl.DataFrame,
) -> pl.DataFrame:
    """Drop columns from `phylogeny_df` that may be invalidated by
    topological operations such as collapsing unifurcations.

    See Also
    --------
    alifestd_drop_topological_sensitivity :
        Pandas-based implementation.
    """
    to_drop = alifestd_check_topological_sensitivity(phylogeny_df)
    if not to_drop:
        return phylogeny_df

    return phylogeny_df.drop(to_drop)
