import typing

import pandas as pd

# Columns that represent ratios or ordinal properties derived from
# origin_time.  These are preserved by uniform shift or rescale operations
# but invalidated by arbitrary reassignment of origin_time values.
_reassign_only_sensitive_cols = frozenset(
    (
        "clade_duration_ratio_sister",
        "clade_fblr_growth_sister",
        "clade_logistic_growth_sister",
        "clade_subtended_duration_ratio_sister",
        "ot_mrca_id",
    )
)

# All columns that may be invalidated by chronological operations.
_chronologically_sensitive_cols = frozenset(
    (
        *_reassign_only_sensitive_cols,
        "ancestor_origin_time",
        "branch_length",
        "clade_duration",
        "clade_faithpd",
        "clade_fblr_growth_children",
        "clade_logistic_growth_children",
        "clade_subtended_duration",
        "edge_length",
        "max_descendant_origin_time",
        "origin_time_delta",
        "ot_mrca_time_of",
        "ot_mrca_time_since",
    )
)


def _get_sensitive_cols(
    shift: bool, rescale: bool, reassign: bool
) -> frozenset:
    """Return the set of sensitive column names for the given operation
    types."""
    if reassign:
        return _chronologically_sensitive_cols
    elif shift or rescale:
        return _chronologically_sensitive_cols - _reassign_only_sensitive_cols
    else:
        return frozenset()


def alifestd_check_chronological_sensitivity(
    phylogeny_df: pd.DataFrame,
    *,
    shift: bool,
    rescale: bool,
    reassign: bool,
) -> typing.List[str]:
    """Return names of columns present in `phylogeny_df` that may be
    invalidated by chronological operations such as coercing chronological
    consistency.

    If no such columns exist, returns an empty list.

    Parameters
    ----------
    phylogeny_df : pandas.DataFrame
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
    alifestd_check_chronological_sensitivity_polars :
        Polars-based implementation.
    """
    sensitive = _get_sensitive_cols(shift, rescale, reassign)
    return [col for col in phylogeny_df.columns if col in sensitive]
