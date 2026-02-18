import typing
import warnings

from ._alifestd_check_topological_sensitivity import (
    alifestd_check_topological_sensitivity,
)


def alifestd_warn_topological_sensitivity(
    phylogeny_df: typing.Any,
    caller: str,
) -> None:
    """Emit a warning if `phylogeny_df` contains columns that may be
    invalidated by topological operations.

    Parameters
    ----------
    phylogeny_df
        A pandas or polars DataFrame.
    caller : str
        Name of the calling function, included in the warning message.

    Input dataframe is not mutated by this operation.
    """
    present_warned = alifestd_check_topological_sensitivity(phylogeny_df)
    if present_warned:
        warnings.warn(
            f"{caller} does not update topology-dependent columns, "
            f"which may be invalidated: {present_warned}. "
            "Use `origin_time` to recalculate branch lengths for "
            "collapsed phylogeny."
        )
