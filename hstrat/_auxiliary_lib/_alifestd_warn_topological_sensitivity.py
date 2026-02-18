import typing
import warnings

import pandas as pd

from ._alifestd_check_topological_sensitivity import (
    alifestd_check_topological_sensitivity,
)


def _alifestd_warn_topological_sensitivity(
    invalidated: typing.List[str],
    caller: str,
    *,
    insert: bool,
    delete: bool,
    update: bool,
) -> None:
    """Private helper: emit a warning listing invalidated columns."""
    if invalidated:
        ops = "/".join(
            name
            for flag, name in [
                (insert, "insert"),
                (delete, "delete"),
                (update, "update"),
            ]
            if flag
        )
        warnings.warn(
            f"{caller} performs {ops} operations that do not update "
            f"topology-dependent columns, which may be invalidated: "
            f"{invalidated}. "
            "Use `origin_time` to recalculate branch lengths for "
            "collapsed phylogeny. To silence this warning, use "
            "alifestd_drop_topological_sensitivity{_polars}."
        )


def alifestd_warn_topological_sensitivity(
    phylogeny_df: pd.DataFrame,
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
    phylogeny_df : pandas.DataFrame
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
    alifestd_warn_topological_sensitivity_polars :
        Polars-based implementation.
    """
    _alifestd_warn_topological_sensitivity(
        alifestd_check_topological_sensitivity(
            phylogeny_df,
            insert=insert,
            delete=delete,
            update=update,
        ),
        caller,
        insert=insert,
        delete=delete,
        update=update,
    )
