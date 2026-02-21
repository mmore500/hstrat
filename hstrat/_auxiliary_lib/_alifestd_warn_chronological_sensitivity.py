import os
import typing
import warnings

import pandas as pd

from ._alifestd_check_chronological_sensitivity import (
    alifestd_check_chronological_sensitivity,
)


def _alifestd_warn_chronological_sensitivity(
    invalidated: typing.List[str],
    caller: str,
    *,
    shift: bool,
    rescale: bool,
    reassign: bool,
) -> None:
    """Private helper: emit a warning listing invalidated columns."""
    if (
        invalidated
        and "HSTRAT_ALIFESTD_WARN_CHRONOLOGICAL_SENSITIVITY_SUPPRESS"
        not in os.environ
    ):
        ops = "/".join(
            name
            for flag, name in [
                (shift, "shift"),
                (rescale, "rescale"),
                (reassign, "reassign"),
            ]
            if flag
        )
        warnings.warn(
            f"{caller} performs {ops} operations that do not update "
            f"chronology-dependent columns, which may be invalidated: "
            f"{invalidated}. "
            "Use `origin_time` to recalculate time-derived columns for "
            "adjusted phylogeny. To silence this warning, use "
            "alifestd_drop_chronological_sensitivity{_polars} or set "
            "HSTRAT_ALIFESTD_WARN_CHRONOLOGICAL_SENSITIVITY_SUPPRESS "
            "environment variable."
        )


def alifestd_warn_chronological_sensitivity(
    phylogeny_df: pd.DataFrame,
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
    phylogeny_df : pandas.DataFrame
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
    alifestd_warn_chronological_sensitivity_polars :
        Polars-based implementation.
    """
    _alifestd_warn_chronological_sensitivity(
        alifestd_check_chronological_sensitivity(
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
