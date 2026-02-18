import typing

import pandas as pd

# Columns that describe the node-to-parent relationship or position in the
# existing hierarchy.  These are ONLY invalidated by update operations
# (changing ancestor relationships), NOT by pure insert (adding new nodes)
# or pure delete (removing entire contiguous branches).
_update_only_sensitive_cols = frozenset((
    "ancestor_origin_time",
    "branch_length",
    "edge_length",
    "node_depth",
    "origin_time_delta",
))

# All columns that may be invalidated by topological operations.
_topologically_sensitive_cols = frozenset((
    *_update_only_sensitive_cols,
    "clade_duration",
    "clade_duration_ratio_sister",
    "clade_fblr_growth_children",
    "clade_fblr_growth_sister",
    "clade_faithpd",
    "clade_leafcount_ratio_sister",
    "clade_logistic_growth_children",
    "clade_logistic_growth_sister",
    "clade_nodecount_ratio_sister",
    "clade_subtended_duration",
    "clade_subtended_duration_ratio_sister",
    "is_left_child",
    "is_right_child",
    "left_child_id",
    "max_descendant_origin_time",
    "num_children",
    "num_descendants",
    "num_leaves",
    "num_leaves_sibling",
    "num_preceding_leaves",
    "ot_mrca_id",
    "ot_mrca_time_of",
    "ot_mrca_time_since",
    "right_child_id",
    "sister_id",
))


def _get_sensitive_cols(
    insert: bool,
    delete: bool,
    update: bool,
) -> frozenset:
    """Return the set of sensitive column names for the given operation
    types."""
    if update:
        return _topologically_sensitive_cols
    elif insert or delete:
        return _topologically_sensitive_cols - _update_only_sensitive_cols
    else:
        return frozenset()


def alifestd_check_topological_sensitivity(
    phylogeny_df: pd.DataFrame,
    *,
    insert: bool,
    delete: bool,
    update: bool,
) -> typing.List[str]:
    """Return names of columns present in `phylogeny_df` that may be
    invalidated by topological operations such as collapsing unifurcations.

    If no such columns exist, returns an empty list.

    Parameters
    ----------
    phylogeny_df : pandas.DataFrame
        The phylogeny as a dataframe in alife standard format.
    insert : bool
        Whether the operation inserts new nodes.
    delete : bool
        Whether the operation deletes nodes.
    update : bool
        Whether the operation updates ancestor relationships.

    Input dataframe is not mutated by this operation.

    See Also
    --------
    alifestd_check_topological_sensitivity_polars :
        Polars-based implementation.
    """
    sensitive = _get_sensitive_cols(insert, delete, update)
    return [
        col for col in phylogeny_df.columns
        if col in sensitive
    ]
