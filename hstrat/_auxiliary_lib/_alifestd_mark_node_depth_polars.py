import argparse
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import polars as pl

from ._alifestd_has_contiguous_ids_polars import (
    alifestd_has_contiguous_ids_polars,
)
from ._alifestd_is_topologically_sorted_polars import (
    alifestd_is_topologically_sorted_polars,
)
from ._alifestd_mark_node_depth_asexual import (
    _alifestd_calc_node_depth_asexual_contiguous,
)
from ._alifestd_try_add_ancestor_id_col_polars import (
    alifestd_try_add_ancestor_id_col_polars,
)
from ._configure_prod_logging import configure_prod_logging
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_mark_node_depth_polars(
    phylogeny_df: pl.DataFrame,
) -> pl.DataFrame:
    """Add column `node_depth`, counting the number of nodes between a
    node and the root.

    Parameters
    ----------
    phylogeny_df : polars.DataFrame or polars.LazyFrame
        The phylogeny as a dataframe in alife standard format.

        Must represent an asexual phylogeny with contiguous ids and
        topologically sorted rows.

    Returns
    -------
    polars.DataFrame
        The phylogeny with an added `node_depth` integer column.

    See Also
    --------
    alifestd_mark_node_depth_asexual :
        Pandas-based implementation.
    """
    logging.info(
        "- alifestd_mark_node_depth_polars: "
        "adding ancestor_id col...",
    )
    phylogeny_df = alifestd_try_add_ancestor_id_col_polars(phylogeny_df)

    if phylogeny_df.lazy().limit(1).collect().is_empty():
        return phylogeny_df.with_columns(
            node_depth=pl.lit(0).cast(pl.Int64),
        )

    logging.info(
        "- alifestd_mark_node_depth_polars: "
        "checking contiguous ids...",
    )
    if not alifestd_has_contiguous_ids_polars(phylogeny_df):
        raise NotImplementedError(
            "non-contiguous ids not yet supported",
        )

    logging.info(
        "- alifestd_mark_node_depth_polars: "
        "checking topological sort...",
    )
    if not alifestd_is_topologically_sorted_polars(phylogeny_df):
        raise NotImplementedError(
            "topologically unsorted rows not yet supported",
        )

    logging.info(
        "- alifestd_mark_node_depth_polars: "
        "extracting ancestor ids...",
    )
    ancestor_ids = (
        phylogeny_df.lazy()
        .select("ancestor_id")
        .collect()
        .to_series()
        .to_numpy()
    )

    logging.info(
        "- alifestd_mark_node_depth_polars: "
        "calculating node depths...",
    )
    node_depths = _alifestd_calc_node_depth_asexual_contiguous(ancestor_ids)

    return phylogeny_df.with_columns(
        node_depth=pl.Series(node_depths),
    )


_raw_description = f"""\
{os.path.basename(__file__)} | \
(hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Add `node_depth` column counting nodes between each node and the root.

Data is assumed to be in alife standard format.

Additional Notes
================
- Requires 'ancestor_id' column (or 'ancestor_list' column from which \
ancestor_id can be derived).

- Use `--eager-read` if modifying data file inplace.

- This CLI entrypoint is experimental and may be subject to change.

See Also
========
hstrat._auxiliary_lib._alifestd_mark_node_depth_asexual :
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
        dfcli_module=(
            "hstrat._auxiliary_lib._alifestd_mark_node_depth_polars"
        ),
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()

    try:
        with log_context_duration(
            "hstrat._auxiliary_lib"
            "._alifestd_mark_node_depth_polars",
            logging.info,
        ):
            _run_dataframe_cli(
                base_parser=parser,
                output_dataframe_op=(alifestd_mark_node_depth_polars),
            )
    except NotImplementedError as e:
        logging.error(
            "- polars op not yet implemented, use pandas op CLI instead",
        )
        raise e
