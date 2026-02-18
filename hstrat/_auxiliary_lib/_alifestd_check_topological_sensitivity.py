import typing


_topologically_sensitive_cols = [
    "ancestor_origin_time",
    "branch_length",
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
    "edge_length",
    "is_left_child",
    "is_right_child",
    "left_child_id",
    "max_descendant_origin_time",
    "node_depth",
    "num_children",
    "num_descendants",
    "num_leaves",
    "num_leaves_sibling",
    "num_preceding_leaves",
    "origin_time_delta",
    "ot_mrca_id",
    "ot_mrca_time_of",
    "ot_mrca_time_since",
    "right_child_id",
    "sister_id",
]


def alifestd_check_topological_sensitivity(
    phylogeny_df: typing.Any,
) -> typing.List[str]:
    """Return names of columns present in `phylogeny_df` that may be
    invalidated by topological operations such as collapsing unifurcations.

    Accepts pandas or polars DataFrames.

    Input dataframe is not mutated by this operation.
    """
    columns = phylogeny_df.columns
    return [col for col in _topologically_sensitive_cols if col in columns]
