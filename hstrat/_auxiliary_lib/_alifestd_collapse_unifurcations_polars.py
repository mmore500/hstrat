import argparse
import logging
import os
import warnings

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import polars as pl

from ._alifestd_assign_contiguous_ids_polars import (
    alifestd_assign_contiguous_ids_polars,
)
from ._alifestd_collapse_unifurcations import _collapse_unifurcations
from ._alifestd_has_contiguous_ids_polars import (
    alifestd_has_contiguous_ids_polars,
)
from ._alifestd_is_topologically_sorted_polars import (
    alifestd_is_topologically_sorted_polars,
)
from ._configure_prod_logging import configure_prod_logging
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_collapse_unifurcations_polars(
    phylogeny_df: pl.DataFrame,
) -> pl.DataFrame:
    """Pare record to bypass organisms with one ancestor and one descendant.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.

    See Also
    --------
    alifestd_collapse_unifurcations :
        Pandas-based implementation.
    """
    schema_names = phylogeny_df.lazy().collect_schema().names()

    warned_cols = [
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
    present_warned = [col for col in warned_cols if col in schema_names]
    if present_warned:
        warnings.warn(
            "alifestd_collapse_unifurcations does not update topology-"
            "dependent columns, which may be invalidated: "
            f"{present_warned}. "
            "Use `origin_time` to recalculate branch lengths for "
            "collapsed phylogeny."
        )

    if "ancestor_list" in schema_names:
        raise NotImplementedError

    logging.info(
        "- alifestd_collapse_unifurcations_polars: "
        "collecting original ids...",
    )
    original_ids = (
        phylogeny_df.lazy().select("id").collect().to_series().to_numpy()
    )

    logging.info(
        "- alifestd_collapse_unifurcations_polars: "
        "checking contiguous ids...",
    )
    if not alifestd_has_contiguous_ids_polars(phylogeny_df):
        logging.info(
            "- alifestd_collapse_unifurcations_polars: assigning ids...",
        )
        phylogeny_df = alifestd_assign_contiguous_ids_polars(phylogeny_df)

    logging.info(
        "- alifestd_collapse_unifurcations_polars: "
        "checking topological sort...",
    )
    if not alifestd_is_topologically_sorted_polars(phylogeny_df):
        raise NotImplementedError(
            "polars topological sort not yet implemented",
        )

    logging.info(
        "- alifestd_collapse_unifurcations_polars: "
        "collecting ancestor_ids...",
    )
    ancestor_ids = (
        phylogeny_df.lazy()
        .select("ancestor_id")
        .collect()
        .to_series()
        .to_numpy()
    )

    logging.info(
        "- alifestd_collapse_unifurcations_polars: calculating reindex...",
    )
    keep_filter, ancestor_ids = _collapse_unifurcations(
        ancestor_ids.copy(),  # must copy to remove read-only flag...
        # ... for numba compatibility
    )

    logging.info(
        "- alifestd_collapse_unifurcations_polars: applying reindex...",
    )
    return phylogeny_df.filter(keep_filter).with_columns(
        id=original_ids[keep_filter],
        ancestor_id=original_ids[ancestor_ids[keep_filter]],
    )


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Pare record to bypass organisms with one ancestor and one descendant.

Data is assumed to be in alife standard format.
Only supports asexual phylogenies.

Additional Notes
================
- Requires 'ancestor_id' column to be present in input DataFrame.

- Use `--eager-read` if modifying data file inplace.

- This CLI entrypoint is experimental and may be subject to change.

See Also
========
hstrat._auxiliary_lib._alifestd_collapse_unifurcations :
    CLI entrypoint for Pandas-based implementation.
"""


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        add_help=False,
        description=format_cli_description(_raw_description),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser = _add_parser_base(
        parser=parser,
        dfcli_module="hstrat._auxiliary_lib._alifestd_collapse_unifurcations_polars",
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()

    try:
        with log_context_duration(
            "hstrat._auxiliary_lib._alifestd_collapse_unifurcations_polars",
            logging.info,
        ):
            _run_dataframe_cli(
                base_parser=parser,
                output_dataframe_op=alifestd_collapse_unifurcations_polars,
            )
    except NotImplementedError as e:
        logging.error(
            "- polars op not yet implemented, use pandas op CLI instead",
        )
        raise e
